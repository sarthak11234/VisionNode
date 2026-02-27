"""
Models package — import all models here so Alembic auto-discovers them.

When Alembic runs `alembic revision --autogenerate`, it inspects Base.metadata
to find all registered tables. By importing every model here, we ensure they're
all registered before Alembic looks.
"""

from app.models.base import Base
from app.models.workspace import Workspace
from app.models.sheet import Sheet
from app.models.row import Row
from app.models.agent_rule import AgentRule
from app.models.agent_log import AgentLog

__all__ = ["Base", "Workspace", "Sheet", "Row", "AgentRule", "AgentLog"]
