import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Database URL configuration (defaults to SQLite if PostgreSQL is unavailable)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./complaints.db")

# Force SQLite if default local postgresql URL cannot connect
def _create_db_engine():
    db_url = os.getenv("DATABASE_URL", "sqlite:///./complaints.db")
    if db_url.startswith("sqlite"):
        return create_engine(db_url, connect_args={"check_same_thread": False})
    
    try:
        engine_inst = create_engine(db_url, pool_pre_ping=True)
        # Test connection
        with engine_inst.connect() as conn:
            pass
        return engine_inst
    except Exception:
        # Fallback to local SQLite file database for development/testing
        sqlite_url = "sqlite:///./complaints.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})


engine = _create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI database session dependency generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
