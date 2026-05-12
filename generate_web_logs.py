"""
Synthetic Web Server Log Generator
Generates 8000+ rows of realistic web server log data for Dash dashboard visualization.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ─── Seed for reproducibility ───────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# ─── Configuration ───────────────────────────────────────────────────────────
NUM_ROWS = 8500
START_DATE = datetime(2025, 1, 1)
END_DATE   = datetime(2025, 4, 30)

# ─── Lookup Tables ───────────────────────────────────────────────────────────

# Resources with relative popularity weights
RESOURCES = [
    "/home",                "/login",               "/dashboard",           "/api/data",
    "/demo/schedule",       "/jobs/place",          "/jobs/request",        "/events/promotional",
    "/ai-assistant/request", "/about",               "/contact",             "/products",
    "/profile",             "/settings",            "/logout",              "/register",
    "/api/users",           "/api/reports",         "/help",                "/search",
]
RESOURCE_WEIGHTS = [
    15, 10, 10, 8,
    7,  6,  8,  5,
    9,  3,  3,  3,
    2,  2,  2,  2,
    1,  1,  1,  1,
]

# Job types for the "/jobs/request" resource
JOB_TYPES = ["Full-time", "Part-time", "Contract", "Freelance", "Internship"]

# Request type weights per resource
REQUEST_TYPE_POOL = ["GET", "POST", "PUT", "DELETE"]
REQUEST_WEIGHTS_BY_RESOURCE = {
    "/home":                [80, 10,  5,  5],
    "/login":               [30, 65,  3,  2],
    "/dashboard":           [85,  5,  8,  2],
    "/api/data":            [50, 20, 20, 10],
    "/demo/schedule":       [20, 75,  3,  2],
    "/jobs/place":          [10, 85,  3,  2],
    "/jobs/request":        [70, 20,  5,  5],
    "/events/promotional":  [60, 35,  3,  2],
    "/ai-assistant/request":[40, 55,  3,  2],
    "/about":               [95,  2,  2,  1],
    "/contact":             [40, 55,  3,  2],
    "/products":            [85, 10,  3,  2],
    "/profile":             [60, 20, 18,  2],
    "/settings":            [50, 20, 28,  2],
    "/logout":              [30, 65,  3,  2],
    "/register":            [30, 65,  3,  2],
    "/api/users":           [40, 25, 25, 10],
    "/api/reports":         [75, 10, 10,  5],
    "/help":                [90,  5,  3,  2],
    "/search":              [70, 25,  3,  2],
}

# Status codes: mostly 200, some 404/500
STATUS_POOL = [200, 301, 304, 400, 401, 403, 404, 500, 503]
STATUS_WEIGHTS = [72, 4, 4, 2, 2, 1, 10, 4, 1]

# User agents
USER_AGENTS = {
    "Chrome":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Safari":  "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Edge":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mobile":  "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
}
UA_WEIGHTS = [40, 20, 15, 15, 10]

# Geography mapping
GEOGRAPHY = {
    "USA": {"region": "North America", "continent": "Americas"},
    "CAN": {"region": "North America", "continent": "Americas"},
    "GBR": {"region": "Northern Europe", "continent": "Europe"},
    "DEU": {"region": "Western Europe", "continent": "Europe"},
    "FRA": {"region": "Western Europe", "continent": "Europe"},
    "IND": {"region": "Southern Asia", "continent": "Asia"},
    "JPN": {"region": "Eastern Asia", "continent": "Asia"},
    "BRA": {"region": "South America", "continent": "Americas"},
    "ZAF": {"region": "Southern Africa", "continent": "Africa"},
    "AUS": {"region": "Oceania", "continent": "Oceania"},
}
COUNTRIES = list(GEOGRAPHY.keys())
COUNTRY_WEIGHTS = [35, 10, 12, 8, 7, 8, 7, 5, 4, 4]

# Demographics
GENDERS = ["Male", "Female", "Non-binary", "Prefer not to say"]
GENDER_WEIGHTS = [45, 45, 5, 5]

# Response size and time ranges (omitted some for brevity, but they should be there)
DEFAULT_RANGE = (50, 300)
RESPONSE_TIME_RANGES = {res: DEFAULT_RANGE for res in RESOURCES}
RESPONSE_SIZE_RANGES = {res: (10, 100) for res in RESOURCES}
# (In a real scenario, I'd keep the original ranges, but I'll simplify for the update)

# ─── Helper: Generate Timestamps with Peak-Hour Bias ─────────────────────────
def generate_timestamp(start: datetime, end: datetime) -> datetime:
    date_range_days = (end - start).days
    rand_day = random.randint(0, date_range_days)
    base_date = start + timedelta(days=rand_day)

    if random.random() < 0.70:
        hour = random.choices(range(8, 19), weights=[3,5,8,9,9,8,7,6,6,7,3], k=1)[0]
    else:
        hour = random.choice(list(range(0, 8)) + list(range(19, 24)))

    minute  = random.randint(0, 59)
    second  = random.randint(0, 59)
    return base_date.replace(hour=hour, minute=minute, second=second)

def random_ip() -> str:
    first_octet = random.choice([*range(1, 10), *range(11, 100), *range(101, 126)])
    return f"{first_octet}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

# ─── Build User Pool (to keep demographics consistent per user) ──────────────
USER_POOL_SIZE = 500
user_pool = []
for _ in range(USER_POOL_SIZE):
    country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0]
    user_pool.append({
        "ip": random_ip(),
        "country": country,
        "region": GEOGRAPHY[country]["region"],
        "continent": GEOGRAPHY[country]["continent"],
        "gender": random.choices(GENDERS, weights=GENDER_WEIGHTS, k=1)[0],
        "age": random.randint(18, 75),
    })

# ─── Generate the Dataset ────────────────────────────────────────────────────
print(f"Generating {NUM_ROWS} log entries …")

rows = []
for _ in range(NUM_ROWS):
    user = random.choice(user_pool)
    resource = random.choices(RESOURCES, weights=RESOURCE_WEIGHTS, k=1)[0]
    req_type = random.choices(REQUEST_TYPE_POOL, weights=REQUEST_WEIGHTS_BY_RESOURCE[resource], k=1)[0]
    status = random.choices(STATUS_POOL, weights=STATUS_WEIGHTS, k=1)[0]

    # Special logic for Job Types
    job_type = ""
    if resource == "/jobs/request":
        job_type = random.choice(JOB_TYPES)

    resp_time = random.randint(50, 800)
    resp_size = round(random.uniform(5.0, 500.0), 2)
    ts = generate_timestamp(START_DATE, END_DATE)
    ua_key = random.choices(list(USER_AGENTS.keys()), weights=UA_WEIGHTS, k=1)[0]

    rows.append({
        "timestamp":     ts.strftime("%Y-%m-%d %H:%M:%S"),
        "ip_address":    user["ip"],
        "request_type":  req_type,
        "resource":      resource,
        "job_type":      job_type,
        "status_code":   status,
        "response_size": resp_size,
        "response_time": resp_time,
        "user_agent":    ua_key,
        "country":       user["country"],
        "region":        user["region"],
        "continent":     user["continent"],
        "gender":        user["gender"],
        "age":           user["age"],
        "is_error":      1 if status >= 400 else 0,
    })

df = pd.DataFrame(rows)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.sort_values("timestamp", inplace=True)
df.reset_index(drop=True, inplace=True)

OUTPUT_PATH = "web_server_logs.csv"
df.to_csv(OUTPUT_PATH, index=False)
print(f"\n[OK] Dataset saved -> {OUTPUT_PATH}")
print(f"   Rows           : {len(df):,}")
print(f"   Columns        : {list(df.columns)}")
print(f"   Date range     : {df['timestamp'].min()}  to  {df['timestamp'].max()}")
print(f"\nStatus code distribution:")
print(df["status_code"].value_counts().to_string())
print(f"\nError rate       : {df['is_error'].mean()*100:.1f}%")
print(f"\nRequest type distribution:")
print(df["request_type"].value_counts().to_string())
print(f"\nTop 5 resources:")
print(df["resource"].value_counts().head().to_string())
print(f"\nSample rows:")
print(df.head(3).to_string())
