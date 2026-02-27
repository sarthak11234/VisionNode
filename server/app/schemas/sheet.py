"""
Sheet Schemas — Validation for sheet creation, column schemas, and responses.

COLUMN SCHEMA VALIDATION:
  Each column is defined as a ColumnDef with:
    - key:     Machine-friendly identifier (e.g., "roll_no")
    - label:   Human-friendly display name (e.g., "Roll Number")
    - type:    One of "string", "number", "dropdown", "boolean"
    - order:   Sort position in the sheet
    - options: Required only for "dropdown" type

  Pydantic validates this structure on every API call, so malformed
  column definitions are rejected before touching the DB.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Column Definition ────────────────────────────────────


class ColumnDef(BaseModel):
    """Schema for a single column in the spreadsheet."""

    key: str = Field(..., min_length=1, max_length=100, examples=["status"])
    label: str = Field(..., min_length=1, max_length=255, examples=["Status"])
    col_type: str = Field(
        ...,
        alias="type",
        pattern="^(string|number|dropdown|boolean)$",
        examples=["dropdown"],
    )
    order: int = Field(0, ge=0)
    options: list[str] | None = Field(
        None,
        examples=[["Pending", "Selected", "Rejected"]],
    )


# ── Request Schemas ──────────────────────────────────────


class SheetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Main Auditions"])
    columns: list[ColumnDef] = Field(default_factory=list)


class SheetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)


class ColumnUpdate(BaseModel):
    """Add, modify, or reorder columns."""

    columns: list[ColumnDef]

class BulkActionRequest(BaseModel):
    """Payload for triggering bulk actions from the frontend."""
    
    row_ids: list[uuid.UUID]
    message: str | None = None
    subject: str | None = None


# ── Response Schemas ─────────────────────────────────────


class SheetResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    column_schema: list[ColumnDef]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SheetListResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
