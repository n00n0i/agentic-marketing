"""PostgreSQL connection manager — production ready."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

import structlog


logger = structlog.get_logger(__name__)

# Singleton engine (set on init)
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def init_engine(database_url: str, pool_size: int = 10, max_overflow: int = 20) -> Engine:
    """Initialize the SQLAlchemy engine. Call once at startup."""
    global _engine, _SessionLocal

    logger.info("db_init", url=database_url.split("@")[-1] if "@" in database_url else "sqlite")

    _engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,  # Verify connection health
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False,
    )

    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine


def get_session() -> Session:
    """Get a database session (dependency injection style)."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_engine() first.")
    return _SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_engine() -> Engine:
    """Get the current engine (for migrations, etc.)."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_engine() first.")
    return _engine