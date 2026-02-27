"""
AgentRule Model — Automation rules that agents follow.

Each rule watches a specific column for a specific value and triggers an action.
Example: "When 'Status' becomes 'Selected', send WhatsApp template 'Welcome_Msg'"

HOW RULE MATCHING WORKS:
  When a row is updated (PATCH /rows/{id}), we check all rules for that sheet.
  For each rule, we compare:
    row.data[rule.trigger_column] == rule.trigger_value

  If matched → enqueue a Celery task with the action config.

  This is a simple "exact match" strategy.
  Alternative: Expression engine (e.g., "score > 80 AND status != 'Rejected'")
    — more powerful but much more complex to parse. We start simple and can
    upgrade to a mini-DSL (Domain Specific Language) later if needed.

ACTION CONFIG (JSONB):
  Stores action-specific settings. Structure varies by action_type:
    - "whatsapp":     {"template": "Welcome_Msg", "phone_column": "phone"}
    - "email":        {"subject": "You're in!", "template_id": "invite_01"}
    - "create_group": {"group_name": "Dance Team 2026"}
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AgentRule(Base):
    __tablename__ = "agent_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sheet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # What column to watch
    trigger_column: Mapped[str] = mapped_column(String(255), nullable=False)

    # What value triggers the action
    trigger_value: Mapped[str] = mapped_column(String(255), nullable=False)

    # Action type: "whatsapp", "email", "create_group"
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Action-specific configuration — see docstring for examples
    action_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Enable/disable without deleting
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────
    sheet: Mapped["Sheet"] = relationship("Sheet", back_populates="agent_rules")

    logs: Mapped[list["AgentLog"]] = relationship(
        "AgentLog", back_populates="rule", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AgentRule {self.action_type} on {self.trigger_column}={self.trigger_value}>"
