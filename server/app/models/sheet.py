"""
Sheet Model — The core spreadsheet entity.

Each sheet lives inside a workspace and has:
  - A flexible column schema stored as JSONB
  - Many rows of data
  - Agent rules that watch for changes

WHY JSONB FOR COLUMN SCHEMA?
  Users can add, remove, and reorder columns dynamically without DB migrations.
  The column_schema is a JSON array like:
    [
      {"key": "name",   "label": "Name",   "type": "string",   "order": 0},
      {"key": "score",  "label": "Score",  "type": "number",   "order": 1},
      {"key": "status", "label": "Status", "type": "dropdown", "order": 2,
       "options": ["Pending", "Selected", "Rejected"]}
    ]

  Alternative: EAV (Entity-Attribute-Value) pattern — a separate table for each
    column value. Much harder to query and 10x slower for reads. JSONB wins here.

  Alternative: MongoDB — native document store, but we'd lose relational
    integrity (FK constraints between sheets ↔ rows ↔ rules).
"""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Sheet(Base):
    __tablename__ = "sheets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Flexible column definitions — see docstring above for structure.
    column_schema: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="sheets")

    rows: Mapped[list["Row"]] = relationship(
        "Row", back_populates="sheet", cascade="all, delete-orphan"
    )

    agent_rules: Mapped[list["AgentRule"]] = relationship(
        "AgentRule", back_populates="sheet", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sheet {self.name}>"
