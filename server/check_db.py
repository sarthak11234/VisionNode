import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.core.database import async_session
from app.models.agent_rule import AgentRule
from app.models.row import Row
from sqlalchemy.future import select

async def check_db():
    print("Checking database...")
    try:
        async with async_session() as db:
            # Check Rows
            res_rows = await db.execute(select(Row))
            rows = res_rows.scalars().all()
            print(f"Found {len(rows)} Rows in DB.")
            for r in rows:
                print(f" - Row {r.id}: {r.data}")

            # Check Rules
            res_rules = await db.execute(select(AgentRule))
            rules = res_rules.scalars().all()
            print(f"Found {len(rules)} Rules in DB.")
            for r in rules:
                print(f" - Rule {r.id}: {r.trigger_column} == {r.trigger_value} -> {r.action_type}")
                
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_db())
