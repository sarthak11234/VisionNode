"""
Alembic environment configuration — ASYNC version.

This file tells Alembic how to connect to the DB and find your models.

KEY CONCEPT: target_metadata
  Alembic compares Base.metadata (your Python models) against the actual DB
  schema. The diff becomes the migration. This is why we import all models
  in app.models.__init__.py — so they register with Base.metadata.

WHY ASYNC?
  Our app uses asyncpg (async driver). Alembic doesn't natively support async,
  so we use run_async_migrations() to bridge the gap. This runs the migration
  inside an async engine context.
"""

import asyncio
from logging.config import fileConfig
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.models import Base  # This imports ALL models via __init__.py
from app.core.config import settings

# Alembic Config object — provides access to alembic.ini values
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what Alembic compares against the live DB
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL without connecting."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Execute migrations against a live DB connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Bridge async engine to Alembic's sync migration runner."""
    connectable = create_async_engine(settings.DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connects to real DB."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
