"""
Row Schemas — Validation for spreadsheet row data.

ROW DATA:
  Row data is a flat dict keyed by column keys:
    {"name": "Sarthak", "score": 85, "status": "Selected"}

  We accept `dict[str, Any]` because column types are dynamic.
  Deep validation (e.g., "score must be a number") happens at the
  service layer by cross-referencing the sheet's column_schema.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Request Schemas ──────────────────────────────────────


class RowCreate(BaseModel):
    data: dict[str, Any] = Field(
        default_factory=dict, examples=[{"name": "Sarthak", "score": 85}]
    )
    row_order: float | None = Field(None, examples=[1.0])


class RowUpdate(BaseModel):
    data: dict[str, Any] | None = Field(None)
    row_order: float | None = Field(None)


class RowBulkCreate(BaseModel):
    """For CSV import — many rows at once."""

    rows: list[RowCreate]


# ── Response Schemas ─────────────────────────────────────


class RowResponse(BaseModel):
    id: uuid.UUID
    sheet_id: uuid.UUID
    data: dict[str, Any]
    row_order: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
