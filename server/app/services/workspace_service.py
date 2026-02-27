"""
Workspace Service — Business logic for workspace operations.

All DB queries live here, not in the router. This makes the logic:
  1. Testable — inject a mock DB session
  2. Reusable — other services can call these functions
  3. Decoupled — router changes don't affect query logic
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


async def create(
    db: AsyncSession, payload: WorkspaceCreate, owner_id: str
) -> Workspace:
    """Insert a new workspace."""
    ws = Workspace(name=payload.name, owner_id=owner_id)
    db.add(ws)
    await db.flush()  # Assigns ID without committing (commit happens in get_db)
    await db.refresh(ws)
    return ws


async def list_by_owner(db: AsyncSession, owner_id: str) -> list[Workspace]:
    """Get all workspaces owned by a user, newest first."""
    result = await db.execute(
        select(Workspace)
        .where(Workspace.owner_id == owner_id)
        .order_by(Workspace.created_at.desc())
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, workspace_id: uuid.UUID) -> Workspace | None:
    """Get a single workspace by ID."""
    return await db.get(Workspace, workspace_id)


async def update(
    db: AsyncSession, workspace_id: uuid.UUID, payload: WorkspaceUpdate
) -> Workspace | None:
    """Partially update a workspace."""
    ws = await db.get(Workspace, workspace_id)
    if not ws:
        return None

    # Only update fields that were explicitly set (not None)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ws, field, value)

    await db.flush()
    await db.refresh(ws)
    return ws


async def delete(db: AsyncSession, workspace_id: uuid.UUID) -> bool:
    """Delete a workspace. Returns True if found and deleted."""
    ws = await db.get(Workspace, workspace_id)
    if not ws:
        return False
    await db.delete(ws)
    await db.flush()
    return True
