"""
Row Service — Business logic for spreadsheet rows.

ORDERING ALGORITHM: Fractional indexing
  When inserting between two rows, we use the midpoint:
    Between row_order 1.0 and 2.0 → new row gets 1.5
    Between 1.5 and 2.0 → 1.75

  This is O(1) — no need to update any other rows.

  Problem: After many insertions, floats lose precision (~15 decimal digits).
  Solution: Periodic rebalancing (re-number all rows as 1.0, 2.0, 3.0...).
  We implement get_next_order() to append at the end by default.

  Alternative: Array-based ordering (store row IDs in an ordered array on
  the sheet). Simpler reads but requires updating the entire array on every
  insert/reorder.
"""

import uuid

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.row import Row
from app.schemas.row import RowCreate, RowUpdate


async def get_next_order(db: AsyncSession, sheet_id: uuid.UUID) -> float:
    """Get the next row_order value (max + 1)."""
    result = await db.execute(
        select(sa_func.coalesce(sa_func.max(Row.row_order), 0.0)).where(
            Row.sheet_id == sheet_id
        )
    )
    return result.scalar_one() + 1.0


async def create(db: AsyncSession, sheet_id: uuid.UUID, payload: RowCreate) -> Row:
    """Create a row. If no row_order given, append at end."""
    order = (
        payload.row_order
        if payload.row_order is not None
        else await get_next_order(db, sheet_id)
    )
    row = Row(sheet_id=sheet_id, data=payload.data, row_order=order)
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


async def bulk_create(
    db: AsyncSession, sheet_id: uuid.UUID, rows: list[RowCreate]
) -> list[Row]:
    """Create many rows at once (CSV import)."""
    base_order = await get_next_order(db, sheet_id)
    new_rows = []
    for i, row_data in enumerate(rows):
        row = Row(
            sheet_id=sheet_id,
            data=row_data.data,
            row_order=row_data.row_order
            if row_data.row_order is not None
            else base_order + i,
        )
        db.add(row)
        new_rows.append(row)
    await db.flush()
    for row in new_rows:
        await db.refresh(row)
    return new_rows


async def list_by_sheet(db: AsyncSession, sheet_id: uuid.UUID) -> list[Row]:
    """Get all rows in a sheet, ordered by row_order."""
    result = await db.execute(
        select(Row).where(Row.sheet_id == sheet_id).order_by(Row.row_order)
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, row_id: uuid.UUID) -> Row | None:
    return await db.get(Row, row_id)


async def update(db: AsyncSession, row_id: uuid.UUID, payload: RowUpdate) -> Row | None:
    """Update row data and/or order. Returns old data for rule comparison."""
    row = await db.get(Row, row_id)
    if not row:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    if "data" in update_data and update_data["data"] is not None:
        # Merge new data into existing (partial cell updates)
        merged = {**row.data, **update_data["data"]}
        row.data = merged
    if "row_order" in update_data and update_data["row_order"] is not None:
        row.row_order = update_data["row_order"]
    await db.flush()
    await db.refresh(row)
    return row


async def delete(db: AsyncSession, row_id: uuid.UUID) -> bool:
    row = await db.get(Row, row_id)
    if not row:
        return False
    await db.delete(row)
    await db.flush()
    return True
