import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define base directory and database file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

# Database connection URL for SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create SQLAlchemy engine with SQLite specific argument for thread safety
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal class instance to create session objects for DB interaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
