from flask import Flask
from .routes import app as app_blueprint

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    app.register_blueprint(app_blueprint)

    return app
