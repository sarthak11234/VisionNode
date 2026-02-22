"""
AgentLog Model — Audit trail for every agent action.

Every time an agent fires (sends a WhatsApp, email, etc.), the result is logged.
This provides:
  1. Transparency — admin sees what the agent did
  2. Debugging — if a message failed, we know why
  3. Idempotency — before firing, check if this rule+row combo already succeeded
     (prevents double-sending)

STATUS VALUES:
  "pending"  → Task queued in Celery
  "success"  → Action completed successfully
  "failed"   → Action failed (error details in `message`)
  "retrying" → Failed once, retry scheduled
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    row_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # "pending", "success", "failed", "retrying"
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Human-readable result or error message
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────
    rule: Mapped["AgentRule"] = relationship("AgentRule", back_populates="logs")

    def __repr__(self) -> str:
        return f"<AgentLog {self.status} rule={self.rule_id}>"
