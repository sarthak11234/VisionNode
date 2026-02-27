"""
Row Router — CRUD endpoints for rows within a sheet.

This is the most critical router because:
  - Every cell edit triggers PATCH /rows/{id}
  - That PATCH is where agent rules get evaluated (Phase 3)
  - CSV import hits the bulk-create endpoint
"""

import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.ws_manager import manager
from app.schemas.row import RowCreate, RowUpdate, RowBulkCreate, RowResponse
from app.services import row_service

router = APIRouter(tags=["rows"])


@router.post(
    "/sheets/{sheet_id}/rows",
    response_model=RowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_row(
    sheet_id: uuid.UUID,
    payload: RowCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a single row in a sheet."""
    row = await row_service.create(db, sheet_id, payload)
    await manager.broadcast(
        sheet_id,
        {
            "event": "row_created",
            "row": RowResponse.model_validate(row).model_dump(mode="json"),
        },
    )
    return row


@router.post(
    "/sheets/{sheet_id}/rows/bulk",
    response_model=list[RowResponse],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_rows(
    sheet_id: uuid.UUID,
    payload: RowBulkCreate,
    db: AsyncSession = Depends(get_db),
):
    """Bulk-create rows (JSON array)."""
    return await row_service.bulk_create(db, sheet_id, payload.rows)


@router.get("/sheets/{sheet_id}/rows", response_model=list[RowResponse])
async def list_rows(
    sheet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all rows in a sheet, ordered by row_order."""
    return await row_service.list_by_sheet(db, sheet_id)


from sqlalchemy import select
from app.models.agent_rule import AgentRule
from app.tasks.agent_tasks import process_agent_rule

@router.patch("/rows/{row_id}", response_model=RowResponse)
async def update_row(
    row_id: uuid.UUID,
    payload: RowUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update row data (cell values) or row_order.
    This is the agent trigger point — Phase 3 will hook rule evaluation here.
    """
    row = await row_service.update(db, row_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
        
    # --- Agent Rule Evaluation ---
    # Phase 4: Iterate over enabled rules for this sheet
    if payload.data:
        # Find all active rules for this sheet
        stmt = select(AgentRule).where(
            AgentRule.sheet_id == row.sheet_id,
            AgentRule.enabled == True
        )
        rules_res = await db.execute(stmt)
        rules = rules_res.scalars().all()
        
        for rule in rules:
            # Check if the trigger column was updated in this payload
            if rule.trigger_column in payload.data:
                # Check if the new value matches the trigger condition
                if str(payload.data[rule.trigger_column]) == str(rule.trigger_value):
                    print(f"Triggering rule '{rule.action_type}' for row {row.id}")
                    # Enqueue LangGraph Celery task
                    process_agent_rule.delay(str(rule.id), str(row.id))

    # --- WebSocket Broadcast ---
    await manager.broadcast(
        row.sheet_id,
        {
            "event": "row_updated",
            "row": RowResponse.model_validate(row).model_dump(mode="json"),
        },
    )
    return row


@router.delete("/rows/{row_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_row(row_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a single row."""
    # Fetch the row first to get sheet_id for broadcast
    row = await row_service.get_by_id(db, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    sheet_id = row.sheet_id
    await row_service.delete(db, row_id)
    await manager.broadcast(sheet_id, {"event": "row_deleted", "row_id": str(row_id)})


# ---------------------------------------------------------------------------
# CSV Import
# ---------------------------------------------------------------------------


@router.post(
    "/sheets/{sheet_id}/import-csv",
    response_model=list[RowResponse],
    status_code=status.HTTP_201_CREATED,
)
async def import_csv(
    sheet_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    """Import rows from a CSV file.

    The CSV must have a header row whose column names match the sheet's
    column keys. Each subsequent row becomes a new Row with data as JSONB.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # utf-8-sig handles BOM from Excel
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    reader = csv.DictReader(io.StringIO(text))
    row_creates = [RowCreate(data=dict(row)) for row in reader]

    if not row_creates:
        raise HTTPException(
            status_code=400, detail="CSV file is empty or has no data rows"
        )

    return await row_service.bulk_create(db, sheet_id, row_creates)
