"""
data_loader.py – Load, validate, and process web server log data.
Supports CSV and Excel files.
"""

import pandas as pd
import numpy as np
import base64
import io

REQUIRED_COLUMNS = {
    "timestamp", "ip_address", "request_type", "resource", "job_type",
    "status_code", "response_size", "response_time",
    "user_agent", "country", "region", "continent", "gender", "age",
    "hour", "day", "is_error",
}

# ─── Public API ──────────────────────────────────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    """Load a CSV or Excel file from disk."""
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    return process_data(df)


def parse_upload_content(contents: str, filename: str) -> pd.DataFrame:
    """Decode a Dash dcc.Upload base64 payload and return a processed DataFrame."""
    content_type, content_string = contents.split(",", 1)
    decoded = base64.b64decode(content_string)
    if filename.endswith(".csv"):
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    else:
        df = pd.read_excel(io.BytesIO(decoded))
    return process_data(df)


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich a raw DataFrame."""
    df = df.copy()

    # ── timestamp ──────────────────────────────────────────────────────────
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.dropna(subset=["timestamp"], inplace=True)
        df["hour"] = df["timestamp"].dt.hour
        df["day"]  = df["timestamp"].dt.day_name()
        df["date"] = df["timestamp"].dt.date
        df["week"] = df["timestamp"].dt.isocalendar().week
        df["month"] = df["timestamp"].dt.month_name()

    # ── numerics ───────────────────────────────────────────────────────────
    for col in ["status_code", "response_size", "response_time", "hour", "age", "is_error"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── derived ────────────────────────────────────────────────────────────
    df["is_error"] = (df["status_code"] >= 400).astype(int)

    # ── strings ────────────────────────────────────────────────────────────
    string_cols = [
        "ip_address", "request_type", "resource", "job_type", "user_agent", 
        "day", "country", "region", "continent", "gender", "month"
    ]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace("nan", "")

    df.dropna(subset=["status_code", "response_time", "response_size"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# ─── Statistics ──────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a dict of top-level KPIs."""
    if df is None or df.empty:
        return {}
    
    # Calculate Sales Indicators
    demos = len(df[df["resource"] == "/demo/schedule"])
    jobs = len(df[df["resource"] == "/jobs/place"])
    ai_requests = len(df[df["resource"] == "/ai-assistant/request"])
    
    return {
        "total_requests":   int(len(df)),
        "unique_ips":       int(df["ip_address"].nunique()),
        "error_rate":       float(round(df["is_error"].mean() * 100, 2)),
        "mean_resp_time":   float(round(df["response_time"].mean(), 1)),
        "std_resp_time":    float(round(df["response_time"].std(), 1)),
        "demo_requests":    int(demos),
        "jobs_placed":      int(jobs),
        "ai_assistant":     int(ai_requests),
    }
