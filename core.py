"""
core.py – Dash application definition and server exposure.
"""

import sys
import os

# Ensure the dashboard directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import dash
import dash_bootstrap_components as dbc

from layout import build_layout
from callbacks import register_callbacks

# ─── App Initialisation ──────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
    ],
    suppress_callback_exceptions=True,
    eager_loading=True,
    title="AI Solutions",
    meta_tags=[
        {"name": "viewport",
         "content": "width=device-width, initial-scale=1"},
        {"name": "description",
         "content": "Interactive web server log analytics dashboard built with Dash."},
    ],
)

# ─── Layout & Callbacks ──────────────────────────────────────────────────────
app.layout = build_layout()
register_callbacks(app)

# Expose server for Gunicorn deployment (Render, Heroku, etc.)
server = app.server

# ─── Dev server ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host="0.0.0.0", port=port)
