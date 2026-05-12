import sys
import os

# --- Simple Root-Based Entry Point ---
# Everything is now in the root directory to ensure Render deployment works perfectly.

try:
    import core
    server = core.server
except ImportError as e:
    # Diagnostic print just in case
    print(f"DEBUG: BASE_DIR={os.path.dirname(os.path.abspath(__file__))}")
    print(f"DEBUG: sys.path={sys.path}")
    print(f"DEBUG: Contents={os.listdir('.')}")
    raise e

# Expose 'app' for Gunicorn (web: gunicorn app:app)
app = server

if __name__ == "__main__":
    from core import app as dash_app
    port = int(os.environ.get("PORT", 8050))
    dash_app.run(debug=True, host="0.0.0.0", port=port)
