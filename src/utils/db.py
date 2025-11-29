from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import settings

# SQLAlchemy Base class (for model definitions)
Base = declarative_base()

# Create engine (sync version)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Session maker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """Dependency-style DB getter for FastAPI / MCP server."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
