# run.py
from flask_backend.create_app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Determine the host to bind to
    if app.config["FLASK_ENV"] == "development":
        # Use '::' to enable IPv6 and IPv4 binding
        host = '::' if os.environ.get('REMOTE') else 'localhost'
        app.run(debug=True, host=host, port=5000)
    else:
        app.run(debug=False, host='::', port=5000)