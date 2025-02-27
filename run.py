# run.py
from flask_backend.create_app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Determine the host to bind to
    if app.config["FLASK_ENV"] == "development":
        # Use '::' to enable IPv6 and IPv4 binding
        host = '0.0.0.0' if os.environ.get('REMOTE') =='1' else '127.0.0.1'
        app.run(debug=True, host=host, port=5000)
    else:
        app.run(debug=False, host='::', port=5000)