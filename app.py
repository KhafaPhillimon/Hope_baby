import sys
import os

# Ensure the current directory is in sys.path so we can import the dashboard package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from dashboard.app import server
except ImportError:
    # Fallback for different environments
    sys.path.insert(0, os.path.join(BASE_DIR, "dashboard"))
    from app import server

# Expose 'app' as an alias for 'server' for Gunicorn (web: gunicorn app:app)
app = server

if __name__ == "__main__":
    from dashboard.app import app as dash_app
    port = int(os.environ.get("PORT", 8050))
    dash_app.run(debug=True, host="0.0.0.0", port=port)
