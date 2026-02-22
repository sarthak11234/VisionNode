"""
Row Model — A single data row in a sheet.

Each row stores its cell values as JSONB keyed by column key:
  {"name": "Sarthak", "score": 85, "status": "Selected"}

WHY JSONB FOR ROW DATA?
  Same reason as column_schema — columns are dynamic. A traditional approach
  would require one SQL column per user-defined column, meaning ALTER TABLE
  on every column add. JSONB avoids this entirely.

  Performance: PostgreSQL GIN indexes on JSONB allow queries like
    "find all rows where data->>'status' = 'Selected'" in O(log n).

ROW ORDERING:
  We use a float-based ordering system instead of integer positions.
  To insert a row between positions 1.0 and 2.0, assign 1.5.
  This avoids rewriting every row's position on insert.

  Alternative: Linked list (prev/next pointers) — harder to query for
    "give me rows in order" (requires recursive CTE).
  Alternative: Integer gaps (1000, 2000, 3000) — works but eventually
    runs out of gaps and needs rebalancing. Float is simpler.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Row(Base):
    __tablename__ = "rows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sheet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Cell data — keys match column_schema[].key
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Float ordering — allows cheap insertions between existing rows.
    row_order: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ────────────────────────────────────
    sheet: Mapped["Sheet"] = relationship("Sheet", back_populates="rows")

    def __repr__(self) -> str:
        return f"<Row {self.id} order={self.row_order}>"
