from flask import Flask
from .routes import register_blueprints
from .config import Config
import psycopg2
from flasgger import Swagger


def create_app():

    app = Flask(__name__)

    swagger = Swagger(app)

    app.config.from_object(Config)

    app.db_connection = psycopg2.connect(Config.DATABASE_URL)

    register_blueprints(app)

    return app
