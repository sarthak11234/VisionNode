"""
Workspace Schemas — Pydantic models for request/response validation.

WHY SEPARATE SCHEMAS FROM ORM MODELS?
  ORM models = how data is stored in the DB.
  Schemas    = how data enters/exits the API.

  This separation lets us:
  1. Hide internal fields (e.g., never expose raw DB IDs in some cases)
  2. Validate input shapes (reject bad requests before they hit the DB)
  3. Version the API without changing the DB

  Alternative: Use ORM models directly — works for tiny apps but couples
  your API contract to your DB schema. One change breaks both.

PATTERN: Create / Response / Update
  - Create schema  → what the client sends to create a resource
  - Response schema → what the API returns (includes id, timestamps)
  - Update schema  → partial updates (all fields optional)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Request Schemas ──────────────────────────────────────


class WorkspaceCreate(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=255, examples=["Dance Auditions 2026"]
    )


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)


# ── Response Schemas ─────────────────────────────────────


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
