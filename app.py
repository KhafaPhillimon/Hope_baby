import sys
import os

# --- Robust Path Resolution for Render ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

# Ensure these are at the front of sys.path
if DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, DASHBOARD_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    # Attempt to import the server from core.py inside the dashboard folder
    import core
    server = core.server
except ImportError as e:
    # If it fails, print debug info for Render logs
    print(f"DEBUG: BASE_DIR={BASE_DIR}")
    print(f"DEBUG: sys.path={sys.path}")
    print(f"DEBUG: Contents of BASE_DIR={os.listdir(BASE_DIR)}")
    if os.path.exists(DASHBOARD_DIR):
        print(f"DEBUG: Contents of DASHBOARD_DIR={os.listdir(DASHBOARD_DIR)}")
    raise ImportError(f"Could not find 'core.py' in {DASHBOARD_DIR}. Error: {e}")

# Expose 'app' as an alias for 'server' for Gunicorn (web: gunicorn app:app)
app = server

if __name__ == "__main__":
    from core import app as dash_app
    port = int(os.environ.get("PORT", 8050))
    dash_app.run(debug=True, host="0.0.0.0", port=port)
