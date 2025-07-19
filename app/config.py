import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    TESTING = os.getenv("FLASK_TESTING", "false").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL")
