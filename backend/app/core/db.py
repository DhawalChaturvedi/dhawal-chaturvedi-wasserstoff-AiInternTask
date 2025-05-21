from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Path to SQLite DB file
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/data/test.db"  # SQLite database file located in backend/data/

# Create an engine instance for the SQLite DB
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal binds the engine to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """
    Dependency function that provides a database session for the lifespan of a request.

    Yields:
        db (Session): SQLAlchemy database session.

    Ensures that the database session is closed after use to prevent connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
