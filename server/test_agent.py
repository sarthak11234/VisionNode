import asyncio
import os
import sys

# Ensure server module is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.core.database import async_session
from app.models.row import Row
from app.services.agent_rule_service import evaluate_rules_for_row
from app.core.worker import execute_agent_rule
from sqlalchemy.future import select

async def trigger_agent():
    print("Connecting to local database...")
    async with async_session() as db:
        # 1. Grab any row
        result = await db.execute(select(Row))
        row = result.scalars().first()
        
        if not row:
            print("❌ No rows exist in the DB! You must add one via the UI.")
            return

        print(f"✅ Found Target Row ID: {row.id}")
        
        # 2. Mutate its data in memory to match our test rule ("Shortlisted")
        mocked_data = dict(row.data)
        mocked_data["Status"] = "Shortlisted" # Ensure this matches a rule you created!
        mocked_data["Phone"] = "+15555555555" # Add your phone here if you want a real test
        mocked_data["Name"] = "VisionNode Tester"
        
        print("🔍 Searching for matching Agent Rules...")
        matched_rules = await evaluate_rules_for_row(db, row.sheet_id, mocked_data)
        
        if not matched_rules:
            print("⚠️ No matching rules found. Did you create a rule for Status == Shortlisted?")
            return
            
        print(f"✅ Found {len(matched_rules)} matching rule(s).")
        
        # 3. Fire it off to the Celery worker
        for rule in matched_rules:
            print(f"🚀 Dispatching Rule {rule.id} to Celery Background Queue...")
            execute_agent_rule.delay(str(row.id), str(rule.id))
            
        print("🎉 Successfully dispatched! Check the other terminal running the worker.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(trigger_agent())
