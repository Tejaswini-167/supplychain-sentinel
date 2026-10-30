import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL

# Load environment variables from backend/.env
load_dotenv()

# Read database configuration
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

# Create database engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)