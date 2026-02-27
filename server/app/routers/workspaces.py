"""
Workspace Router — CRUD endpoints for workspaces.

PATTERN: Router → Service (thin controller pattern)
  Routers handle HTTP concerns (status codes, path params, dependencies).
  Business logic lives in the service layer, keeping routers thin and testable.

  Alternative: Fat controllers (all logic in router functions) — works for
  small apps but becomes unmaintainable as logic grows. Thin controllers
  are the industry standard for production APIs.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.services import workspace_service

router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"],
)

# NOTE: owner_id is hardcoded for now. In Phase 5, Clerk auth middleware
# will extract the real user ID from the JWT token.
TEMP_OWNER_ID = "dev-user-001"


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new workspace."""
    return await workspace_service.create(db, payload, owner_id=TEMP_OWNER_ID)


@router.get("/", response_model=list[WorkspaceResponse])
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    """List all workspaces for the current user."""
    return await workspace_service.list_by_owner(db, owner_id=TEMP_OWNER_ID)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a single workspace by ID."""
    ws = await workspace_service.get_by_id(db, workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: uuid.UUID,
    payload: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a workspace's name."""
    ws = await workspace_service.update(db, workspace_id, payload)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(workspace_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a workspace and all its sheets/rows (cascade)."""
    deleted = await workspace_service.delete(db, workspace_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found")
