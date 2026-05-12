"""
charts.py – All Plotly figure factories for the dashboard.
Each function accepts a filtered DataFrame and returns a go.Figure.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─── Shared theme ────────────────────────────────────────────────────────────
PALETTE = px.colors.qualitative.Bold
BG      = "#0a0b14"
PAPER   = "#161829"
GRID    = "rgba(139, 92, 246, 0.1)"
TEXT    = "#f8fafc"

LAYOUT_BASE = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    font=dict(family="Inter, sans-serif", color=TEXT, size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
)


def _apply_base(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(title=dict(text=title, font=dict(size=15, color=TEXT)),
                      **LAYOUT_BASE)
    return fig


# ─── 1. Requests per Hour ────────────────────────────────────────────────────
def requests_per_hour(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Requests per Hour")
    counts = df.groupby("hour").size().reindex(range(24), fill_value=0)
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values,
        marker=dict(
            color=counts.values,
            colorscale=[[0, GRID], [1, C["accent"]]],
            showscale=False,
        ),
        hovertemplate="Hour %{x}:00<br>Requests: %{y}<extra></extra>",
    ))
    fig.update_xaxes(title="Hour of Day", tickmode="linear", dtick=1)
    fig.update_yaxes(title="Request Count")
    return _apply_base(fig, "Requests per Hour")


# ─── 2. Top Resources ────────────────────────────────────────────────────────
def top_resources(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if df.empty:
        return _empty("Top Resources")
    counts = df["resource"].value_counts().head(top_n).sort_values()
    fig = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h",
        marker_color=PALETTE[:len(counts)],
        hovertemplate="%{y}<br>Requests: %{x}<extra></extra>",
    ))
    fig.update_xaxes(title="Request Count")
    fig.update_yaxes(title="")
    return _apply_base(fig, f"Top {top_n} Accessed Resources")


# ─── 3. Status Code Distribution ─────────────────────────────────────────────
def status_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Status Code Distribution")
    counts = df["status_code"].astype(str).value_counts()
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values,
        hole=0.45,
        marker=dict(colors=PALETTE),
        hovertemplate="%{label}<br>Count: %{value}<br>%{percent}<extra></extra>",
        textfont=dict(color=TEXT),
    ))
    fig.update_layout(paper_bgcolor=PAPER,
                      font=dict(family="Inter, sans-serif", color=TEXT),
                      margin=dict(l=20, r=20, t=50, b=20),
                      legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
                      title=dict(text="Status Code Distribution",
                                 font=dict(size=15, color=TEXT)))
    return fig


# ─── 4. Request Type Distribution ────────────────────────────────────────────
def request_type_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Request Type Distribution")
    counts = df["request_type"].value_counts()
    colors = {"GET": "#4ade80", "POST": "#60a5fa",
              "PUT": "#f59e0b", "DELETE": "#f87171"}
    marker_colors = [colors.get(lbl, "#a78bfa") for lbl in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values,
        hole=0.45,
        marker=dict(colors=marker_colors),
        hovertemplate="%{label}<br>Count: %{value}<br>%{percent}<extra></extra>",
        textfont=dict(color=TEXT),
    ))
    fig.update_layout(paper_bgcolor=PAPER,
                      font=dict(family="Inter, sans-serif", color=TEXT),
                      margin=dict(l=20, r=20, t=50, b=20),
                      legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
                      title=dict(text="Request Type Distribution",
                                 font=dict(size=15, color=TEXT)))
    return fig


# ─── 5. Response Time vs Response Size ───────────────────────────────────────
def response_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Response Time vs Size")
    sample = df.sample(min(2000, len(df)), random_state=1)
    color_map = {"200": "#4ade80", "404": "#f59e0b",
                 "500": "#f87171", "304": "#60a5fa"}
    status_str = sample["status_code"].astype(str)
    colors = [color_map.get(s, "#a78bfa") for s in status_str]
    fig = go.Figure(go.Scatter(
        x=sample["response_time"],
        y=sample["response_size"],
        mode="markers",
        marker=dict(size=5, color=colors, opacity=0.65),
        customdata=status_str,
        hovertemplate=(
            "Response Time: %{x} ms<br>"
            "Response Size: %{y} KB<br>"
            "Status: %{customdata}<extra></extra>"
        ),
    ))
    fig.update_xaxes(title="Response Time (ms)")
    fig.update_yaxes(title="Response Size (KB)")
    return _apply_base(fig, "Response Time vs Response Size")


# ─── 6. Requests Over Time (trend & forecast) ──────────────────────────────────
def requests_over_time(df: pd.DataFrame) -> go.Figure:
    if df.empty or "date" not in df.columns:
        return _empty("Requests Over Time")
    
    daily = df.groupby("date").size().reset_index(name="count")
    daily["date"] = pd.to_datetime(daily["date"])
    
    fig = px.scatter(
        daily, x="date", y="count", 
        trendline="ols",
        trendline_color_override="#f59e0b",
        labels={"date": "Date", "count": "Request Count"},
        title="Daily Request Trend with OLS Forecast"
    )
    
    fig.update_traces(
        marker=dict(size=6, color="#60a5fa", opacity=0.7),
        selector=dict(mode="markers")
    )
    
    fig.update_traces(
        line=dict(width=3, dash="dash"),
        selector=dict(mode="lines")
    )
    
    fig.update_layout(
        hovermode="x unified",
        **LAYOUT_BASE
    )
    fig.update_layout(title=dict(text="Traffic Forecasting (Daily Trend & OLS Projection)", font=dict(size=15, color=TEXT)))
    return fig


# ─── 7. Error Rate by Resource ───────────────────────────────────────────────
def error_rate_by_resource(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Error Rate by Resource")
    grp = df.groupby("resource")["is_error"].agg(["sum", "count"])
    grp["error_rate"] = (grp["sum"] / grp["count"] * 100).round(2)
    grp = grp.sort_values("error_rate", ascending=True)
    fig = go.Figure(go.Bar(
        x=grp["error_rate"], y=grp.index, orientation="h",
        marker=dict(
            color=grp["error_rate"],
            colorscale=[[0, "#4ade80"], [0.5, "#f59e0b"], [1, "#f87171"]],
            showscale=True,
            colorbar=dict(title="%", tickfont=dict(color=TEXT)),
        ),
        hovertemplate="%{y}<br>Error Rate: %{x:.1f}%<extra></extra>",
    ))
    fig.update_xaxes(title="Error Rate (%)")
    fig.update_yaxes(title="")
    return _apply_base(fig, "Error Rate by Resource")


# ─── 8. User Agent Distribution ──────────────────────────────────────────────
def user_agent_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Browser Distribution")
    counts = df["user_agent"].value_counts()
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values,
        marker_color=PALETTE[:len(counts)],
        hovertemplate="%{x}<br>Requests: %{y}<extra></extra>",
    ))
    fig.update_xaxes(title="Browser")
    fig.update_yaxes(title="Request Count")
    return _apply_base(fig, "Browser / User Agent Distribution")

# ─── 9. Geographic Map ───────────────────────────────────────────────────────
def global_map(df: pd.DataFrame) -> go.Figure:
    if df.empty or "country" not in df.columns:
        return _empty("Global Traffic")
    
    counts = df.groupby("country").size().reset_index(name="requests")
    fig = px.choropleth(
        counts,
        locations="country",
        locationmode="country names",
        color="requests",
        color_continuous_scale=[[0, PAPER], [1, C["accent"]]],
        title="Global Traffic Distribution"
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#2a2d3e",
            bgcolor="#1a1d27",
            projection_type="equirectangular"
        ),
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(family="Inter, sans-serif", color=TEXT),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    fig.update_layout(title=dict(font=dict(size=15, color=TEXT)))
    return fig


# ─── 10. Sales Indicators ────────────────────────────────────────────────────
def sales_indicators_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Sales Indicators")
    
    indicators = {
        "Demos": len(df[df["resource"] == "/demo/schedule"]),
        "Jobs": len(df[df["resource"] == "/jobs/place"]),
        "AI Assist": len(df[df["resource"] == "/ai-assistant/request"]),
        "Promo": len(df[df["resource"] == "/events/promotional"]),
    }
    
    fig = go.Figure(go.Bar(
        x=list(indicators.keys()),
        y=list(indicators.values()),
        marker_color=[C["green"], C["yellow"], C["accent"], C["red"]],
        hovertemplate="%{x}<br>Count: %{y}<extra></extra>"
    ))
    return _apply_base(fig, "Key Sales Performance Indicators")


# ─── 11. Demographics (Gender) ──────────────────────────────────────────────
def demographics_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Demographics")
    
    counts = df["gender"].value_counts()
    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.6,
        marker=dict(colors=PALETTE),
    ))
    fig.update_layout(showlegend=True, **LAYOUT_BASE)
    fig.update_layout(title=dict(text="Gender Distribution", font=dict(size=15, color=TEXT)))
    return fig


# ─── 12. Weekly Traffic ──────────────────────────────────────────────────────
def weekly_traffic(df: pd.DataFrame) -> go.Figure:
    if df.empty or "week" not in df.columns:
        return _empty("Weekly Distribution")
    
    counts = df.groupby("week").size()
    fig = go.Figure(go.Bar(
        x=[f"Week {w}" for w in counts.index],
        y=counts.values,
        marker_color=C["blue"],
    ))
    return _apply_base(fig, "Distribution by Time Period (Weekly)")


# ─── 13. Monthly Traffic ─────────────────────────────────────────────────────
def monthly_traffic(df: pd.DataFrame) -> go.Figure:
    if df.empty or "month" not in df.columns:
        return _empty("Monthly Distribution")
    
    # Sort months correctly
    months_order = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
    counts = df["month"].value_counts().reindex(months_order).dropna()
    
    fig = go.Figure(go.Bar(
        x=counts.index,
        y=counts.values,
        marker_color=C["accent2"],
    ))
    return _apply_base(fig, "Distribution by Time Period (Monthly)")


# ─── 14. Job Types Distribution ──────────────────────────────────────────────
def job_types_chart(df: pd.DataFrame) -> go.Figure:
    jobs_df = df[df["job_type"] != ""]
    if jobs_df.empty:
        return _empty("Job Types requested")
    
    counts = jobs_df["job_type"].value_counts()
    fig = go.Figure(go.Bar(
        x=counts.index,
        y=counts.values,
        marker_color=PALETTE,
    ))
    return _apply_base(fig, "Distribution of Job Types Requested")


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _empty(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=TEXT)),
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(family="Inter, sans-serif", color=TEXT),
        annotations=[dict(text="No data available", x=0.5, y=0.5,
                          xref="paper", yref="paper",
                          showarrow=False, font=dict(size=14, color="#6b7280"))],
    )
    return fig

# Need to import colors from layout
from layout import C
