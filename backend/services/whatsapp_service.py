import random
import time
import pywhatkit as kit
import platform
import asyncio
from typing import List
from schemas import Participant

# Safety toggle: Set to True to actually send messages. 
# For dev/demo, we might want to default to False or specific AllowList.
ENABLE_REAL_SENDING = True

async def send_invites_orchestrator(participants: List[Participant], group_link: str = "https://chat.whatsapp.com/EXAMPLE"):
    """
    Orchestrates the sending of WhatsApp messages with human-like delays.
    """
    results = []
    
    print(f"🚀 Starting Automation for {len(participants)} participants...")
    
    for p in participants:
        if p.status == 'sent':
            continue
            
        if '??' in p.phone or len(p.phone) < 10:
            print(f"⚠️ Skipping invalid number: {p.name} ({p.phone})")
            p.status = 'failed'
            results.append(p)
            continue

        # Format number (assume India +91 for now as per Context)
        phone_number = p.phone.strip().replace(" ", "")
        if not phone_number.startswith("+"):
            phone_number = f"+91{phone_number}"
            
        message = f"Hey {p.name}, loved your audition for {p.act}! Join our official group here: {group_link}"
        
        try:
            if ENABLE_REAL_SENDING:
                # PyWhatKit opens web.whatsapp.com. 
                # wait_time=15 (time to load page), tab_close=True, close_time=3
                # We wrap this in a blocking call executor because pywhatkit is blocking
                await asyncio.to_thread(
                    kit.sendwhatmsg_instantly,
                    phone_no=phone_number, 
                    message=message, 
                    wait_time=10, 
                    tab_close=True, 
                    close_time=4
                )
                
                # Add random human-like delay between messages (10-20s)
                delay = random.randint(10, 20)
                print(f"✅ Sent to {p.name}. Waiting {delay}s...")
                await asyncio.sleep(delay)
            else:
                # Dry Run
                print(f"[DRY RUN] Would send to {phone_number}: {message}")
                await asyncio.sleep(1)

            p.status = 'sent'
            
        except Exception as e:
            print(f"❌ Failed to send to {p.name}: {e}")
            p.status = 'failed'
            
        results.append(p)
        
    print("🏁 Automation Complete.")
    return results
