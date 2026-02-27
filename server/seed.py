import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.core.database import async_session
from app.models.workspace import Workspace
from app.models.sheet import Sheet
from app.models.row import Row
from app.models.agent_rule import AgentRule
from app.core.worker import execute_agent_rule
from sqlalchemy.future import select

async def seed_db():
    print("Seeding database...")
    try:
        async with async_session() as db:
            # 1. Create Workspace
            ws = Workspace(name="Test Workspace", owner_id="test_user")
            db.add(ws)
            await db.flush()
            
            # 2. Create Sheet
            sheet = Sheet(workspace_id=ws.id, name="Test Sheet", column_schema=[{"name": "Status"}, {"name": "Phone"}, {"name": "Name"}])
            db.add(sheet)
            await db.flush()
            
            # 3. Create Rule
            rule = AgentRule(
                sheet_id=sheet.id,
                trigger_column="Status",
                trigger_value="Shortlisted",
                action_type="whatsapp",
                action_config={"messageTemplate": "Hi {{Name}}, you are {{Status}}! Contact: {{Phone}}"},
                enabled=True
            )
            db.add(rule)
            await db.flush()

            # 4. Create Row
            row = Row(
                sheet_id=sheet.id,
                row_order=1.0,
                data={"Status": "Shortlisted", "Phone": "9999999999", "Name": "Gemini Tester"}
            )
            db.add(row)
            await db.commit()
            
            print(f"✅ Seeded Workspace: {ws.id}")
            print(f"✅ Seeded Sheet: {sheet.id}")
            print(f"✅ Seeded Rule: {rule.id}")
            print(f"✅ Seeded Row: {row.id}")
            
            print(f"🚀 Dispatching Celery Rule to Queue...")
            execute_agent_rule.delay(str(row.id), str(rule.id))
            print("Done! Check Celery worker logs.")
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_db())
