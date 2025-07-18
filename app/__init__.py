from flask import Flask
from .routes import register_blueprints
from .config import Config


def create_app():
    app = flask(__name__)
    app.config.from_object(Config)

    register_blueprints(app)

    return app
