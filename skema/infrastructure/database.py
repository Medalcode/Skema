"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# Base para todos los modelos
Base = declarative_base()

# Configuración de base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://skema:skema@localhost:5432/skema_db"
)

# Engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No connection pooling por ahora
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency injection para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Crea todas las tablas"""
    Base.metadata.create_all(bind=engine)
