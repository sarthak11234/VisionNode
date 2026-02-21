"""
Database session management.

We use SQLAlchemy's async engine (via asyncpg driver) for non-blocking DB access.

Why async?
  FastAPI is async-first. If we used a synchronous DB driver, every DB query
  would block the entire event loop, killing concurrency. asyncpg is the
  fastest PostgreSQL driver for Python — benchmarks show ~3x faster than
  psycopg2 for simple queries.

  Alternative: psycopg3 (async mode) — also good, but asyncpg has a longer
  track record with SQLAlchemy async.

Pattern: "Dependency Injection via generator"
  get_db() is a FastAPI dependency. Each request gets its own session,
  which is committed/rolled-back and closed automatically.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in dev mode
    pool_size=20,  # Max concurrent connections
    max_overflow=10,  # Extra connections under load
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a DB session per request."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
