# run.py
from flask_backend.create_app import create_app
import os

app = create_app()

if __name__ == "__main__":
    if app.config["FLASK_ENV"] == "development":
        app.run(debug=True, 
                host='0.0.0.0' if os.environ.get('REMOTE') else 'localhost',
                port=5000)
    else:
        app.run(debug=False)