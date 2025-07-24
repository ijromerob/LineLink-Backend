from flask import Flask
from .routes import register_blueprints
from .config import Config
from flasgger import Swagger
from flask_cors import CORS


def create_app():

    app = Flask(__name__)

    Swagger(app)

    app.config.from_object(Config)

    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    register_blueprints(app)

    return app
