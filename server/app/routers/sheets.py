"""
Sheet Router — CRUD endpoints for sheets within a workspace.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.sheet import (
    SheetCreate,
    SheetUpdate,
    ColumnUpdate,
    SheetResponse,
    SheetListResponse,
)
from app.services import sheet_service

router = APIRouter(tags=["sheets"])


@router.post(
    "/workspaces/{workspace_id}/sheets",
    response_model=SheetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sheet(
    workspace_id: uuid.UUID,
    payload: SheetCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new sheet in a workspace with optional column definitions."""
    return await sheet_service.create(db, workspace_id, payload)


@router.get(
    "/workspaces/{workspace_id}/sheets",
    response_model=list[SheetListResponse],
)
async def list_sheets(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all sheets in a workspace."""
    return await sheet_service.list_by_workspace(db, workspace_id)


@router.get("/sheets/{sheet_id}", response_model=SheetResponse)
async def get_sheet(sheet_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a sheet with its full column schema."""
    sheet = await sheet_service.get_by_id(db, sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return sheet


@router.patch("/sheets/{sheet_id}", response_model=SheetResponse)
async def update_sheet(
    sheet_id: uuid.UUID,
    payload: SheetUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update sheet metadata (name)."""
    sheet = await sheet_service.update(db, sheet_id, payload)
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return sheet


@router.put("/sheets/{sheet_id}/columns", response_model=SheetResponse)
async def update_columns(
    sheet_id: uuid.UUID,
    payload: ColumnUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Replace the column schema (add/remove/reorder columns)."""
    sheet = await sheet_service.update_columns(db, sheet_id, payload)
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return sheet


@router.delete("/sheets/{sheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sheet(sheet_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a sheet and all its rows (cascade)."""
    deleted = await sheet_service.delete(db, sheet_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sheet not found")
