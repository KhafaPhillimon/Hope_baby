"""
callbacks.py – All Dash callback definitions.
Imported and registered by app.py via register_callbacks(app).
"""

import io
import os
import pandas as pd
from dash import Input, Output, State, callback_context, no_update, dcc
from dash.exceptions import PreventUpdate

from data_loader import load_data, parse_upload_content, compute_kpis
import charts

# Path to the default dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
DEFAULT_CSV = os.path.join(BASE_DIR, "web_server_logs.csv")
if not os.path.exists(DEFAULT_CSV):
    DEFAULT_CSV = os.path.join(PARENT_DIR, "web_server_logs.csv")


def register_callbacks(app):

    # ── 1. Authentication Callback ───────────────────────────────────────────
    @app.callback(
        Output("auth-store", "data"),
        Output("login-error", "children"),
        Input("btn-login", "n_clicks"),
        Input("btn-logout", "n_clicks"),
        State("login-user", "value"),
        State("login-pass", "value"),
        State("auth-store", "data"),
        prevent_initial_call=True
    )
    def handle_auth(n_login, n_logout, user, password, auth_data):
        ctx = callback_context
        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else ""

        if "btn-logout" in triggered:
            return {"is_logged_in": False}, ""

        if "btn-login" in triggered:
            if user == "admin@aisolutions.com" and password == "Admin123":
                return {"is_logged_in": True}, ""
            else:
                return no_update, "Invalid email or password."
        
        return no_update, no_update

    # ── Visibility Toggle based on Auth ──────────────────────────────────────
    @app.callback(
        Output("login-screen", "style"),
        Output("main-content", "style"),
        Input("auth-store", "data")
    )
    def toggle_screens(auth_data):
        if auth_data and auth_data.get("is_logged_in"):
            return {"display": "none"}, {"display": "block"}
        return {"display": "flex", "justifyContent": "center", "alignItems": "center", "height": "100vh", "position": "fixed", "width": "100%", "top": "0", "left": "0", "zIndex": "1000", "background": "#0a0b14"}, {"display": "none"}


    # ── 2. Load Data (default button) ────────────────────────────────────────
    @app.callback(
        Output("store-full-data",  "data"),
        Output("filter-continent", "options"),
        Output("filter-region",    "options"),
        Output("filter-country",   "options"),
        Output("filter-gender",    "options"),
        Output("filter-resource",  "options"),
        Input("btn-load-default",  "n_clicks"),
        prevent_initial_call=False,
    )
    def load_dataset(n_default):
        df = None

        try:
            df = load_data(DEFAULT_CSV)
        except Exception:
            raise PreventUpdate

        def to_opts(series):
            return [{"label": str(v), "value": str(v)} for v in sorted(series.dropna().unique())]

        return (
            df.to_json(date_format="iso", orient="split"),
            to_opts(df["continent"]),
            to_opts(df["region"]),
            to_opts(df["country"]),
            to_opts(df["gender"]),
            to_opts(df["resource"]),
        )

    # ── 3. Apply Filters ──────────────────────────────────────────────────
    @app.callback(
        Output("store-data", "data"),
        Input("btn-apply", "n_clicks"),
        Input("btn-reset", "n_clicks"),
        Input("store-full-data", "data"),
        State("filter-continent", "value"),
        State("filter-region", "value"),
        State("filter-country", "value"),
        State("filter-gender", "value"),
        State("filter-age", "value"),
        State("filter-resource", "value"),
        prevent_initial_call=False,
    )
    def apply_filters(n_apply, n_reset, full_json, conts, regs, counts, genders, age_range, resources):
        if not full_json:
            raise PreventUpdate

        ctx = callback_context
        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else ""

        df = pd.read_json(io.StringIO(full_json), orient="split")
        
        if "btn-reset" in triggered:
            return full_json

        # Apply hierarchical and demographic filters
        if conts:    df = df[df["continent"].isin(conts)]
        if regs:     df = df[df["region"].isin(regs)]
        if counts:   df = df[df["country"].isin(counts)]
        if genders:  df = df[df["gender"].isin(genders)]
        if age_range: df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
        if resources: df = df[df["resource"].isin(resources)]

        return df.to_json(date_format="iso", orient="split")

    # ── 4. Update KPI Cards ──────────────────────────────────────────────────
    @app.callback(
        Output("kpi-total",   "children"),
        Output("kpi-demos",   "children"),
        Output("kpi-jobs",    "children"),
        Output("kpi-ai",      "children"),
        Output("kpi-mean-rt", "children"),
        Output("kpi-std-rt",  "children"),
        Input("store-data",   "data"),
        prevent_initial_call=False,
    )
    def update_kpis(data_json):
        if not data_json: return ("—",) * 6
        df = pd.read_json(io.StringIO(data_json), orient="split")
        k = compute_kpis(df)
        return (
            f"{k.get('total_requests', 0):,}",
            f"{k.get('demo_requests', 0):,}",
            f"{k.get('jobs_placed', 0):,}",
            f"{k.get('ai_assistant', 0):,}",
            f"{k.get('mean_resp_time', 0):.0f} ms",
            f"{k.get('std_resp_time', 0):.0f} ms",
        )

    # ── 5. Update Charts ─────────────────────────────────────────────────────
    @app.callback(
        Output("chart-hour", "figure"),
        Output("chart-sales-indicators", "figure"),
        Output("chart-demographics", "figure"),
        Output("chart-map", "figure"),
        Output("chart-weekly", "figure"),
        Output("chart-monthly", "figure"),
        Output("chart-trend", "figure"),
        Output("chart-job-types", "figure"),
        Output("chart-resources", "figure"),
        Output("chart-req-type", "figure"),
        Output("chart-status", "figure"),
        Output("table-raw", "data"),
        Output("table-raw", "columns"),
        Input("store-data", "data"),
    )
    def update_charts(data_json):
        if not data_json:
            e = charts._empty
            return (e("Hour"), e("Indicators"), e("Gender"), e("Map"),
                    e("Weekly"), e("Monthly"), e("Trend"), e("Jobs"), e("Res"), e("Req"), e("Status"), [], [])

        df = pd.read_json(io.StringIO(data_json), orient="split")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        
        return (
            charts.requests_per_hour(df),
            charts.sales_indicators_chart(df),
            charts.demographics_chart(df),
            charts.global_map(df),
            charts.weekly_traffic(df),
            charts.monthly_traffic(df),
            charts.requests_over_time(df),
            charts.job_types_chart(df),
            charts.top_resources(df),
            charts.request_type_distribution(df),
            charts.status_distribution(df),
            df.to_dict("records"),
            [{"name": i, "id": i} for i in df.columns if i != "timestamp_iso"] # Exclude internal columns if any
        )

