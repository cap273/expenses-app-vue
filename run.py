from flask_backend.create_app import create_app

app = create_app()

if __name__ == "__main__":
    if app.config["FLASK_ENV"] == "development":
        app.run(debug=True, port=5000)
    else:
        app.run(debug=False)