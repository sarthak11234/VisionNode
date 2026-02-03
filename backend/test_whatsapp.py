import asyncio
from schemas import Participant
from services.whatsapp_service import send_invites_orchestrator

async def test():
    print("Test: Starting WhatsApp Service Test...")
    p = Participant(
        name="Test User",
        phone="1234567890", # Replace with user's number if they want real test, but this will fail validation likely inside service if we have checks
        act="Testing",
        custom_message="Hello from Python script!"
    )
    
    # We need to mock or change the phone number validation in service if it checks for real numbers?
    # Service checks: if '??' in p.phone or len(p.phone) < 10:
    
    try:
        results = await send_invites_orchestrator([p])
        print("Test Result:", results)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test())
