from flask import Flask
from .routes import register_blueprints
from .config import Config
from flasgger import Swagger


def create_app():

    app = Flask(__name__)

    swagger = Swagger(app)

    app.config.from_object(Config)

    register_blueprints(app)

    return app
