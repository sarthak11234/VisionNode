"""
Sheet Service — Business logic for sheets and their columns.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sheet import Sheet
from app.schemas.sheet import SheetCreate, SheetUpdate, ColumnUpdate


async def create(
    db: AsyncSession, workspace_id: uuid.UUID, payload: SheetCreate
) -> Sheet:
    """Create a new sheet with initial column schema."""
    sheet = Sheet(
        workspace_id=workspace_id,
        name=payload.name,
        # Convert ColumnDef Pydantic models → dicts for JSONB storage
        column_schema=[col.model_dump(by_alias=True) for col in payload.columns],
    )
    db.add(sheet)
    await db.flush()
    await db.refresh(sheet)
    return sheet


async def list_by_workspace(db: AsyncSession, workspace_id: uuid.UUID) -> list[Sheet]:
    """List all sheets in a workspace."""
    result = await db.execute(
        select(Sheet)
        .where(Sheet.workspace_id == workspace_id)
        .order_by(Sheet.created_at.desc())
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, sheet_id: uuid.UUID) -> Sheet | None:
    return await db.get(Sheet, sheet_id)


async def update(
    db: AsyncSession, sheet_id: uuid.UUID, payload: SheetUpdate
) -> Sheet | None:
    sheet = await db.get(Sheet, sheet_id)
    if not sheet:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sheet, field, value)
    await db.flush()
    await db.refresh(sheet)
    return sheet


async def update_columns(
    db: AsyncSession, sheet_id: uuid.UUID, payload: ColumnUpdate
) -> Sheet | None:
    """Replace the entire column schema."""
    sheet = await db.get(Sheet, sheet_id)
    if not sheet:
        return None
    sheet.column_schema = [col.model_dump(by_alias=True) for col in payload.columns]
    await db.flush()
    await db.refresh(sheet)
    return sheet


async def delete(db: AsyncSession, sheet_id: uuid.UUID) -> bool:
    sheet = await db.get(Sheet, sheet_id)
    if not sheet:
        return False
    await db.delete(sheet)
    await db.flush()
    return True
