"""
layout.py – Dash layout definition.
All HTML structure, KPI cards, filter panel, and chart placeholders live here.
"""

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from logo_const import LOGO_BASE64

# ─── Color tokens ─────────────────────────────────────────────────────────────
C = {
    "bg":       "#0a0b14", 
    "navbar":   "#0f1020",
    "surface":  "#161829", 
    "surface2": "#1e2136", 
    "border":   "rgba(139, 92, 246, 0.15)", 
    "accent":   "#8b5cf6", 
    "accent2":  "#a855f7", 
    "green":    "#10b981",
    "yellow":   "#f59e0b",
    "red":      "#ef4444",
    "blue":     "#3b82f6",
    "text":     "#f8fafc",
    "muted":    "#a0aec0",
}

CARD_STYLE = {
    "background":   C["surface"],
    "borderRadius": "12px",
    "border":       f"1px solid {C['border']}",
    "padding":      "20px",
    "marginBottom": "16px",
}

FILTER_STYLE = {
    "background":   C["surface2"],
    "borderRadius": "10px",
    "border":       f"1px solid {C['border']}",
    "padding":      "14px 18px",
    "marginBottom": "12px",
}


# ─── KPI Card helper ─────────────────────────────────────────────────────────
def kpi_card(card_id: str, label: str, fa_class: str, color: str) -> dbc.Col:
    """fa_class: Font Awesome class string e.g. 'fa-solid fa-chart-bar'"""
    return dbc.Col(
        html.Div([
            html.I(className=fa_class,
                   style={"fontSize": "24px", "color": color,
                          "marginBottom": "8px", "display": "block"}),
            html.Div(label, style={"fontSize": "11px", "color": C["muted"],
                                   "textTransform": "uppercase",
                                   "letterSpacing": "0.08em",
                                   "marginBottom": "4px"}),
            html.Div(id=card_id, children="—",
                     style={"fontSize": "26px", "fontWeight": "700",
                            "color": color}),
        ], style={**CARD_STYLE, "textAlign": "center"}),
        xs=12, sm=6, md=4, lg=2,
    )


# ─── Main Layout ─────────────────────────────────────────────────────────────
# ─── Main Layout ─────────────────────────────────────────────────────────────
def build_layout() -> html.Div:
    return html.Div(
        style={"background": C["bg"], "minHeight": "100vh",
               "fontFamily": "Inter, sans-serif", "color": C["text"]},
        children=[
            # ── Auth Store ──
            dcc.Store(id="auth-store", data={"is_logged_in": False}, storage_type="session"),

            # ── Login Screen Overlay ──
            html.Div(id="login-screen", children=[
                html.Div([
                    html.Div([
                        html.Img(src=f"data:image/png;base64,{LOGO_BASE64}", style={"height": "80px", "marginBottom": "24px"}),
                        html.H2("AI Solutions", style={"fontWeight": "700", "marginBottom": "5px"}),
                        html.P("Enter your credentials to access the dashboard", style={"color": C["muted"], "fontSize": "13px", "marginBottom": "30px"}),
                    ], style={"textAlign": "center"}),
                    
                    html.Div([
                        html.Label("Username", style={"fontSize": "12px", "color": C["muted"], "marginBottom": "5px", "display": "block"}),
                        dbc.Input(id="login-user", value="admin@aisolutions.com", placeholder="admin@aisolutions.com", type="text", style={"marginBottom": "15px", "background": C["surface2"], "border": f"1px solid {C['border']}", "color": "white"}),
                        
                        html.Label("Password", style={"fontSize": "12px", "color": C["muted"], "marginBottom": "5px", "display": "block"}),
                        dbc.Input(id="login-pass", value="Admin123", placeholder="Admin123", type="password", style={"marginBottom": "25px", "background": C["surface2"], "border": f"1px solid {C['border']}", "color": "white"}),
                        
                        html.Button("Sign In", id="btn-login", n_clicks=0, style={
                            "width": "100%", "padding": "12px", "background": C["accent"], "color": "white", "border": "none", "borderRadius": "8px", "fontWeight": "700", "fontSize": "14px"
                        }),
                        html.Div(id="login-error", style={"color": C["red"], "marginTop": "15px", "textAlign": "center", "fontSize": "13px"})
                    ])
                ], style={
                    "width": "400px", "padding": "50px", "background": C["surface"], "borderRadius": "20px", "border": f"1px solid {C['border']}", "boxShadow": "0 20px 50px rgba(0,0,0,0.5)"
                })
            ], style={
                "display": "flex", "justifyContent": "center", "alignItems": "center", "height": "100vh", "position": "fixed", "width": "100%", "top": "0", "left": "0", "zIndex": "1000", "background": C["bg"]
            }),

            # ── Main Content Container ──
            html.Div(id="main-content", style={"display": "none"}, children=[

                # ── Hidden stores ───────────────────────────────────────────────
                dcc.Store(id="store-data"),
                dcc.Store(id="store-full-data"),
                dcc.Download(id="download-dataframe-csv"),

                # ── Top Nav (Futuristic BI Navbar) ──────────────────────────────────
                html.Div([
                    html.Div([
                        html.Img(src=f"data:image/png;base64,{LOGO_BASE64}", style={
                            "height": "42px", 
                            "marginRight": "18px", 
                            "borderRadius": "8px",
                            "boxShadow": f"0 0 20px {C['border']}", # Soft purple glow
                            "filter": "drop-shadow(0 0 8px rgba(139, 92, 246, 0.3))"
                        }),
                        html.Span("AI Solutions", style={
                            "fontSize": "22px", 
                            "fontWeight": "700", 
                            "letterSpacing": "-0.01em",
                            "color": "white",
                            "textShadow": "0 0 10px rgba(139, 92, 246, 0.2)"
                        }),
                    ], style={"display": "flex", "alignItems": "center"}),
                    
                    html.Div([
                        html.Button([
                            html.I(className="fa-solid fa-right-from-bracket", style={"marginRight": "7px"}),
                            "Sign Out"
                        ], id="btn-logout", style={"background": "transparent", "color": C["red"], "border": f"1px solid {C['red']}", "borderRadius": "6px", "padding": "6px 15px", "fontSize": "12px", "fontWeight": "600"})
                    ], style={"display": "flex", "alignItems": "center"})
                ], style={
                    "display": "flex", 
                    "justifyContent": "space-between", 
                    "alignItems": "center", 
                    "padding": "15px 30px", 
                    "background": C["navbar"], 
                    "borderBottom": f"1px solid {C['border']}", # Sleek thin purple divider
                    "position": "sticky",
                    "top": "0",
                    "zIndex": "1000",
                    "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.4)"
                }),

                # ── Main content ─────────────────────────────────────────────────
                html.Div(style={"padding": "24px 32px"}, children=[
                    dbc.Row([
                        # ── LEFT SIDEBAR: Filters ─────────────────────
                        dbc.Col(width=12, lg=3, children=[
                            html.Div([
                                html.Div([
                                    html.I(className="fa-solid fa-database", style={"marginRight": "7px", "color": C["accent"]}),
                                    "Data Control"
                                ], style={"fontSize": "11px", "fontWeight": "700", "color": C["muted"], "marginBottom": "15px", "textTransform": "uppercase"}),
                                html.Button("Load Fresh Dataset", id="btn-load-default", n_clicks=0, style={
                                    "width": "100%", "background": C["accent"], "color": "white", "border": "none", "borderRadius": "8px", "padding": "12px", "fontWeight": "700", "fontSize": "13px"
                                }),
                            ], style=CARD_STYLE),

                            html.Div([
                                html.Div([
                                    html.I(className="fa-solid fa-sliders", style={"marginRight": "7px", "color": C["accent"]}),
                                    "Global Filters"
                                ], style={"fontSize": "11px", "fontWeight": "700", "color": C["muted"], "marginBottom": "15px", "textTransform": "uppercase"}),
                                
                                _filter_label("Geographic Hierarchy"),
                                dcc.Dropdown(id="filter-continent", placeholder="Select Continent", multi=True, style=_dd_style()),
                                dcc.Dropdown(id="filter-region", placeholder="Select Region", multi=True, style=_dd_style()),
                                dcc.Dropdown(id="filter-country", placeholder="Select Country", multi=True, style=_dd_style()),
                                
                                _filter_label("Demographics"),
                                dcc.Dropdown(id="filter-gender", options=[{"label": g, "value": g} for g in ["Male", "Female", "Non-binary", "Prefer not to say"]], placeholder="Select Gender", multi=True, style=_dd_style()),
                                html.Div("Age Range: 18 - 80", id="age-label", style={"fontSize": "11px", "color": C["muted"], "marginTop": "10px"}),
                                dcc.RangeSlider(id="filter-age", min=18, max=80, step=1, value=[18, 80], marks={18: '18', 40: '40', 60: '60', 80: '80'}),
                                
                                _filter_label("Sales Dimensions"),
                                dcc.Dropdown(id="filter-resource", placeholder="Select Service Type", multi=True, style=_dd_style()),
                                
                                html.Button("Apply Analysis", id="btn-apply", n_clicks=0, style={
                                    "width": "100%", "marginTop": "25px", "background": C["surface2"], "color": C["text"], "border": f"1px solid {C['accent']}", "borderRadius": "8px", "padding": "12px", "fontWeight": "700"
                                }),
                                html.Button("Reset Filters", id="btn-reset", n_clicks=0, style={
                                    "width": "100%", "marginTop": "10px", "background": "transparent", "color": C["muted"], "border": "none", "fontSize": "12px"
                                }),
                            ], style=CARD_STYLE),
                        ]),

                        # ── RIGHT MAIN AREA ────────────────────────────────────
                        dbc.Col(width=12, lg=9, children=[
                            # KPI row
                            dbc.Row([
                                kpi_card("kpi-total",   "Total Requests",    "fa-solid fa-chart-line",      C["blue"]),
                                kpi_card("kpi-demos",   "Demo Requests",     "fa-solid fa-calendar-check",  C["green"]),
                                kpi_card("kpi-jobs",    "Jobs Placed",       "fa-solid fa-briefcase",       C["yellow"]),
                                kpi_card("kpi-ai",      "AI Requests",       "fa-solid fa-robot",           C["accent"]),
                                kpi_card("kpi-mean-rt", "Mean Resp Time",    "fa-solid fa-gauge-high",      C["blue"]),
                                kpi_card("kpi-std-rt",  "Std Dev Resp Time", "fa-solid fa-chart-area",      C["accent2"]),
                            ], className="g-3"),

                            # Tabs
                            dbc.Tabs([
                                dbc.Tab(label="Business Overview", tab_id="tab-overview", children=[
                                    html.Div(style={"paddingTop": "20px"}, children=[
                                        dbc.Row([
                                            dbc.Col(html.Div(dcc.Graph(id="chart-hour"), style=CARD_STYLE), width=12, md=7),
                                            dbc.Col(html.Div(dcc.Graph(id="chart-sales-indicators"), style=CARD_STYLE), width=12, md=5),
                                        ], className="g-3"),
                                        dbc.Row([
                                            dbc.Col(html.Div(dcc.Graph(id="chart-demographics"), style=CARD_STYLE), width=12),
                                        ], className="g-3"),
                                    ])
                                ]),
                                dbc.Tab(label="Global Traffic Distribution", tab_id="tab-geo", children=[
                                    html.Div(style={"paddingTop": "20px"}, children=[
                                        dbc.Row([
                                            dbc.Col(html.Div(dcc.Graph(id="chart-map"), style={**CARD_STYLE, "height": "600px"}), width=12),
                                        ], className="g-3"),
                                    ])
                                ]),
                                dbc.Tab(label="Temporal Distribution", tab_id="tab-time", children=[
                                    html.Div(style={"paddingTop": "20px"}, children=[
                                        dbc.Row([
                                            dbc.Col(html.Div(dcc.Graph(id="chart-weekly"), style=CARD_STYLE), width=12, md=6),
                                            dbc.Col(html.Div(dcc.Graph(id="chart-monthly"), style=CARD_STYLE), width=12, md=6),
                                        ], className="g-3"),
                                        dbc.Row([
                                            dbc.Col(html.Div(dcc.Graph(id="chart-trend"), style=CARD_STYLE), width=12),
                                        ], className="g-3"),
                                    ])
                                ]),
                                dbc.Tab(label="Service & Job Analytics", tab_id="tab-jobs", children=[
                                    html.Div(style={"paddingTop": "20px"}, children=[
                                        dbc.Row([
                                            dbc.Col(html.Div(dcc.Graph(id="chart-job-types"), style=CARD_STYLE), width=12, md=6),
                                            dbc.Col(html.Div(dcc.Graph(id="chart-resources"), style=CARD_STYLE), width=12, md=6),
                                        ], className="g-3"),
                                        dbc.Row([
                                            dbc.Col(html.Div(dcc.Graph(id="chart-req-type"), style=CARD_STYLE), width=12, md=6),
                                            dbc.Col(html.Div(dcc.Graph(id="chart-status"), style=CARD_STYLE), width=12, md=6),
                                        ], className="g-3"),
                                    ])
                                ]),
                                dbc.Tab(label="Raw Log Exploration", tab_id="tab-raw", children=[
                                    html.Div(style={"paddingTop": "20px"}, children=[
                                        html.Div([
                                            html.Div([
                                                html.I(className="fa-solid fa-table", style={"marginRight": "10px", "color": C["accent"]}),
                                                "Dataset Viewer (Filtered)"
                                            ], style={"fontSize": "14px", "fontWeight": "700", "marginBottom": "15px"}),
                                            dash_table.DataTable(
                                                id="table-raw",
                                                page_size=15,
                                                style_table={"overflowX": "auto"},
                                                style_header={
                                                    "backgroundColor": C["surface2"],
                                                    "color": C["text"],
                                                    "fontWeight": "700",
                                                    "border": f"1px solid {C['border']}"
                                                },
                                                style_cell={
                                                    "backgroundColor": C["surface"],
                                                    "color": C["text"],
                                                    "border": f"1px solid {C['border']}",
                                                    "textAlign": "left",
                                                    "padding": "10px",
                                                    "fontSize": "12px"
                                                },
                                                style_data_conditional=[{
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": C["bg"]
                                                }],
                                            )
                                        ], style=CARD_STYLE)
                                    ])
                                ]),
                            ], active_tab="tab-overview", style={"marginTop": "15px"}),
                        ]),
                    ]),
                ]),

            ])
        ]
    )

def _filter_label(text: str) -> html.Div:
    return html.Div(text, style={
        "fontSize": "10px", "fontWeight": "700", "color": C["muted"],
        "marginBottom": "4px", "marginTop": "12px",
        "textTransform": "uppercase", "letterSpacing": "0.06em",
    })

def _dd_style() -> dict:
    return {
        "background":    "#1a1d27",
        "color":         C["text"],
        "borderColor":   C["border"],
        "marginBottom":  "8px",
        "fontSize":      "13px",
    }
