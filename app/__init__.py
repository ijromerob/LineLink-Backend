from flask import Flask
from .routes import register_blueprints
from .config import Config
from flasgger import Swagger
from flask_cors import CORS

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "LineLink API",
        "description": "API documentation for LineLink",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: **Bearer &lt;token&gt;**",
        }
    },
    "security": [{"Bearer": []}],
}


def create_app():

    app = Flask(__name__)

    Swagger(app, template=swagger_template)

    app.config.from_object(Config)

    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    register_blueprints(app)

    return app
