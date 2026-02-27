"""
AgentRule Service — Business logic for automation rules.

Follows the same thin-service pattern as workspace/sheet/row services.
Also includes a helper to evaluate rules against a row update (used in Phase 3).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_rule import AgentRule
from app.models.agent_log import AgentLog
from app.schemas.agent_rule import AgentRuleCreate, AgentRuleUpdate


async def create(
    db: AsyncSession, sheet_id: uuid.UUID, payload: AgentRuleCreate
) -> AgentRule:
    """Create a new automation rule for a sheet."""
    rule = AgentRule(
        sheet_id=sheet_id,
        trigger_column=payload.trigger_column,
        trigger_value=payload.trigger_value,
        action_type=payload.action_type,
        action_config=payload.action_config,
        enabled=payload.enabled,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


async def list_by_sheet(db: AsyncSession, sheet_id: uuid.UUID) -> list[AgentRule]:
    """Get all rules for a given sheet."""
    result = await db.execute(
        select(AgentRule)
        .where(AgentRule.sheet_id == sheet_id)
        .order_by(AgentRule.created_at.desc())
    )
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, rule_id: uuid.UUID) -> AgentRule | None:
    return await db.get(AgentRule, rule_id)


async def update(
    db: AsyncSession, rule_id: uuid.UUID, payload: AgentRuleUpdate
) -> AgentRule | None:
    rule = await db.get(AgentRule, rule_id)
    if not rule:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    await db.flush()
    await db.refresh(rule)
    return rule


async def delete(db: AsyncSession, rule_id: uuid.UUID) -> bool:
    rule = await db.get(AgentRule, rule_id)
    if not rule:
        return False
    await db.delete(rule)
    await db.flush()
    return True


async def list_logs(db: AsyncSession, rule_id: uuid.UUID) -> list[AgentLog]:
    """Get all execution logs for a rule, newest first."""
    result = await db.execute(
        select(AgentLog)
        .where(AgentLog.rule_id == rule_id)
        .order_by(AgentLog.created_at.desc())
    )
    return list(result.scalars().all())


async def evaluate_rules_for_row(
    db: AsyncSession, sheet_id: uuid.UUID, row_data: dict
) -> list[AgentRule]:
    """Find all enabled rules that match the current row data.

    This is the core matching logic used in Phase 3 when a row is updated.
    Returns the list of matching rules so the caller can enqueue Celery tasks.
    """
    rules = await list_by_sheet(db, sheet_id)
    matched = []
    for rule in rules:
        if not rule.enabled:
            continue
        cell_value = row_data.get(rule.trigger_column)
        if str(cell_value) == rule.trigger_value:
            matched.append(rule)
    return matched
