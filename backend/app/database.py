"""Database engine and session configuration.

Supports:
- Local PostgreSQL (development)
- Neon PostgreSQL with SSL (production)
"""

import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings


def _get_connect_args():
    """Return SSL connect_args for Neon (cloud) databases."""
    url = settings.DATABASE_URL
    if "neon.tech" in url or "sslmode=require" in url:
        # Neon requires SSL
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return {"ssl": ssl_context}
    return {}


def _get_sync_connect_args():
    """Return SSL connect_args for sync engine (psycopg2)."""
    url = settings.DATABASE_URL
    if "neon.tech" in url or "sslmode=require" in url:
        return {"sslmode": "require"}
    return {}


# Async engine configuration
def _create_async_engine():
    url = settings.async_database_url
    kwargs = {
        "echo": settings.DEBUG,
        "pool_pre_ping": True,
        "connect_args": _get_connect_args(),
    }
    if not url.startswith("sqlite"):
        kwargs["pool_size"] = 20
        kwargs["max_overflow"] = 10
    return create_async_engine(url, **kwargs)


# Sync engine configuration
def _create_sync_engine():
    url = settings.sync_database_url
    kwargs = {
        "echo": False,
        "connect_args": _get_sync_connect_args(),
    }
    if not url.startswith("sqlite"):
        kwargs["pool_size"] = 5
    return create_engine(url, **kwargs)


async_engine = _create_async_engine()

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

sync_engine = _create_sync_engine()
SyncSessionLocal = sessionmaker(bind=sync_engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency injection for async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
