"""
SQLAlchemy Declarative Base.

All ORM models inherit from this Base class. It provides:
  - Automatic table name generation from class name
  - A shared metadata object that Alembic uses to detect schema changes

Why Declarative style over Core/Table style?
  Declarative = Python classes map directly to DB tables. More readable,
  IDE-friendly, and works naturally with type hints.
  Core style = raw Table() objects. More explicit but verbose.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
