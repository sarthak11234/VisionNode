"""
AgentRule Schemas — Validation for automation rule configuration.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Request Schemas ──────────────────────────────────────


class AgentRuleCreate(BaseModel):
    trigger_column: str = Field(..., min_length=1, examples=["status"])
    trigger_value: str = Field(..., min_length=1, examples=["Selected"])
    action_type: str = Field(
        ...,
        pattern="^(whatsapp|email|create_group)$",
        examples=["whatsapp"],
    )
    action_config: dict[str, Any] = Field(
        default_factory=dict,
        examples=[{"template": "Welcome_Msg", "phone_column": "phone"}],
    )
    enabled: bool = True


class AgentRuleUpdate(BaseModel):
    trigger_column: str | None = None
    trigger_value: str | None = None
    action_type: str | None = Field(None, pattern="^(whatsapp|email|create_group)$")
    action_config: dict[str, Any] | None = None
    enabled: bool | None = None


# ── Response Schemas ─────────────────────────────────────


class AgentRuleResponse(BaseModel):
    id: uuid.UUID
    sheet_id: uuid.UUID
    trigger_column: str
    trigger_value: str
    action_type: str
    action_config: dict[str, Any]
    enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}
