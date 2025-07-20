import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up connection
database_url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(database_url)
