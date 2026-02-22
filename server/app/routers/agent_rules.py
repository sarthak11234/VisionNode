"""
AgentRule Router — CRUD endpoints for automation rules.

Rules are scoped to a sheet. When a row is updated, rules for that sheet
are evaluated. If a match is found, the configured action fires.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.agent_rule import AgentRuleCreate, AgentRuleUpdate, AgentRuleResponse
from app.schemas.agent_log import AgentLogResponse
from app.services import agent_rule_service

router = APIRouter(tags=["agent-rules"])


@router.post(
    "/sheets/{sheet_id}/rules",
    response_model=AgentRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rule(
    sheet_id: uuid.UUID,
    payload: AgentRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create an automation rule for a sheet."""
    return await agent_rule_service.create(db, sheet_id, payload)


@router.get("/sheets/{sheet_id}/rules", response_model=list[AgentRuleResponse])
async def list_rules(
    sheet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all rules for a sheet."""
    return await agent_rule_service.list_by_sheet(db, sheet_id)


@router.get("/rules/{rule_id}", response_model=AgentRuleResponse)
async def get_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a single rule by ID."""
    rule = await agent_rule_service.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.patch("/rules/{rule_id}", response_model=AgentRuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    payload: AgentRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a rule (trigger, action, enabled state)."""
    rule = await agent_rule_service.update(db, rule_id, payload)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a rule and its logs (cascade)."""
    deleted = await agent_rule_service.delete(db, rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")


@router.get("/rules/{rule_id}/logs", response_model=list[AgentLogResponse])
async def list_rule_logs(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get execution logs for a specific rule."""
    return await agent_rule_service.list_logs(db, rule_id)
