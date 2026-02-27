import asyncio
import sys
import os

# Add the server directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import async_session
from app.models.workspace import Workspace
from app.models.sheet import Sheet
from app.models.row import Row
from app.models.agent_rule import AgentRule
from sqlalchemy import select

async def seed():
    async with async_session() as db:
        print("Seeding database...")
        
        # 1. Check if workspace exists
        res = await db.execute(select(Workspace).where(Workspace.name == "Demo Workspace"))
        ws = res.scalar_one_or_none()
        
        if not ws:
            ws = Workspace(name="Demo Workspace", owner_id="dev-user-001")
            db.add(ws)
            await db.commit()
            print(f"Created Workspace: {ws.id}")
        else:
            print(f"Workspace exists: {ws.id}")
            
        # 2. Check if Sheet exists
        res = await db.execute(select(Sheet).where(Sheet.workspace_id == ws.id))
        sheet = res.scalar_one_or_none()
        
        if not sheet:
            sheet = Sheet(
                workspace_id=ws.id,
                name="Auditions 2026",
                column_schema=[
                    {"key": "name", "label": "Name", "type": "text"},
                    {"key": "email", "label": "Email", "type": "text"},
                    {"key": "phone", "label": "Phone", "type": "text"},
                    {"key": "status", "label": "Status", "type": "select"},
                ]
            )
            db.add(sheet)
            await db.commit()
            print(f"Created Sheet: {sheet.id}")
        else:
            print(f"Sheet exists: {sheet.id}")
            
        # 3. Add Demo Rows
        res = await db.execute(select(Row).where(Row.sheet_id == sheet.id))
        rows = res.scalars().all()
        
        if not rows:
            demo_data = [
                {"name": "Alice Smith", "email": "alice@example.com", "phone": "+1234567890", "status": "Pending"},
                {"name": "Bob Jones", "email": "bob@example.com", "phone": "+1987654321", "status": "Pending"},
            ]
            for i, data in enumerate(demo_data):
                db.add(Row(sheet_id=sheet.id, data=data, row_order=float(i)))
            await db.commit()
            print("Created Demo Rows")
        else:
            print(f"Rows exist: {len(rows)}")
            
        # 4. Add Agent Rules
        res = await db.execute(select(AgentRule).where(AgentRule.sheet_id == sheet.id))
        rules = res.scalars().all()
        
        if not rules:
            rule1 = AgentRule(
                sheet_id=sheet.id,
                trigger_column="status",
                trigger_value="Shortlisted",
                action_type="email",
                action_config={"template": "You are shortlisted!"},
                enabled=True
            )
            rule2 = AgentRule(
                sheet_id=sheet.id,
                trigger_column="status",
                trigger_value="Shortlisted",
                action_type="whatsapp",
                action_config={"message": "Congrats!"},
                enabled=True
            )
            db.add_all([rule1, rule2])
            await db.commit()
            print("Created Agent Rules")
        else:
            print(f"Agent Rules exist: {len(rules)}")
            
        print("Seeding complete! Start your servers and visit the frontend.")

if __name__ == "__main__":
    asyncio.run(seed())
