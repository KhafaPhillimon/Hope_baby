import sys
import os

# Ensure the current directory and the dashboard directory are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

dashboard_path = os.path.join(BASE_DIR, "dashboard")
if dashboard_path not in sys.path:
    sys.path.insert(0, dashboard_path)

try:
    # Try importing as a package first
    from dashboard.core import server
except ImportError:
    # Try direct import if dashboard is not seen as a package
    from core import server

# Expose 'app' as an alias for 'server' for Gunicorn (web: gunicorn app:app)
app = server

if __name__ == "__main__":
    try:
        from dashboard.core import app as dash_app
    except ImportError:
        from core import app as dash_app
        
    port = int(os.environ.get("PORT", 8050))
    dash_app.run(debug=True, host="0.0.0.0", port=port)
