"""
AgentLog Schemas — Response-only (logs are created by the agent, not the user).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AgentLogResponse(BaseModel):
    id: uuid.UUID
    rule_id: uuid.UUID
    row_id: uuid.UUID | None
    status: str
    message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
