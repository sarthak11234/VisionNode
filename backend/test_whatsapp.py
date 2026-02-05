import asyncio
from services.messaging.local_whatsapp import LocalMessageService

async def test():
    print("Test: Starting WhatsApp Service Test...")
    p = {
        "name": "Test User",
        "phone": "1234567890", 
        "act": "Testing",
        "customMessage": "Hello from Python script!",
        "status": "pending"
    }
    
    service = LocalMessageService()
    # service.enable_sending = False # Uncomment for dry run
    
    try:
        # Service expects list of dicts
        stats = await service.send_batch([p])
        print("Test Result:", stats)
        print("Updated Participant:", p)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test())
