"""
Database configuration and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from skema.core.config import settings

# Base para todos los modelos
Base = declarative_base()

# Configuración de base de datos asíncrona
# Aseguramos que la URL use asyncpg si es postgresql
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

# Engine asíncrono
engine = create_async_engine(
    db_url,
    poolclass=NullPool,  # No connection pooling por ahora
    echo=settings.SQL_ECHO
)

# Session factory asíncrono
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

async def get_db():
    """Dependency injection para FastAPI"""
    async with SessionLocal() as db:
        yield db

async def init_db():
    """Crea todas las tablas"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
