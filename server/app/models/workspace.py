"""
Workspace Model — Top-level organizer for sheets.

A Workspace groups related sheets together. Think of it like a "project folder."
Example: "Dance Auditions 2026", "Tech Fest Registrations"

Each workspace belongs to one owner (Clerk user ID) and contains many sheets.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    # ── Primary Key ──────────────────────────────────────
    # Why UUID over auto-increment integer?
    #   1. No sequential guessing (security)
    #   2. Can generate IDs client-side before DB insert
    #   3. Safe for distributed systems (no ID collisions)
    #   Alternative: ULID — sortable + random, but less ecosystem support.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Clerk user ID — links to the authenticated user who owns this workspace.
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────
    sheets: Mapped[list["Sheet"]] = relationship(
        "Sheet", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workspace {self.name}>"
