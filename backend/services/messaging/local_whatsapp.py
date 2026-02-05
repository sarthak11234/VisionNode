import random
import time
import pywhatkit as kit
import asyncio
from typing import List, Dict, Any
from ..interfaces import IMessagingService

class LocalMessageService(IMessagingService):
    def __init__(self):
        self.enable_sending = True

    async def send_invite(self, phone: str, message: str) -> bool:
        """
        Sends a single WhatsApp message using Local PyWhatKit.
        NOTE: This opens a browser tab.
        """
        if not self.enable_sending:
            print(f"[DRY RUN] Would send to {phone}: {message}")
            return True

        try:
            # Format number
            phone_number = phone.strip().replace(" ", "")
            if not phone_number.startswith("+"):
                phone_number = f"+91{phone_number}"

            print(f"Attempting to send to {phone_number}...")
            
            # Blocking call in thread
            await asyncio.to_thread(
                kit.sendwhatmsg_instantly,
                phone_no=phone_number, 
                message=message, 
                wait_time=20, 
                tab_close=True, 
                close_time=4
            )
            return True
        except Exception as e:
            print(f"❌ Failed to send to {phone}: {e}")
            return False

    async def send_batch(self, participants: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Orchestrates batch sending with delays.
        """
        stats = {"sent": 0, "failed": 0}
        
        print(f"🚀 Starting Automation for {len(participants)} participants...")
        
        for p in participants:
            if p.get('status') == 'sent':
                continue
                
            if '??' in p['phone'] or len(p['phone']) < 10:
                print(f"⚠️ Skipping invalid number: {p['name']} ({p['phone']})")
                p['status'] = 'failed'
                stats["failed"] += 1
                continue

            # Construct Message (Logic moved here from global)
            # Use custom message if exists, else default template
            if p.get('customMessage'):
                message = p['customMessage']
            else:
                message = self._get_default_template(p['name'])
            
            success = await self.send_invite(p['phone'], message)
            
            if success:
                p['status'] = 'sent'
                stats["sent"] += 1
                # Human delay
                delay = random.randint(10, 20)
                print(f"✅ Sent to {p['name']}. Waiting {delay}s...")
                await asyncio.sleep(delay)
            else:
                p['status'] = 'failed'
                stats["failed"] += 1
                
        print("🏁 Automation Complete.")
        return stats

    def _get_default_template(self, name: str) -> str:
        return f"""Hey {name} 👋
First of all, thank you for showing up for the auditions — really appreciate the effort and energy you all brought in 🙌

This is Sarthak Chavan
Media Secretary, DYPCOEI
Technical Head – Karandak & Annual Events.

For the next step, we need you to mail your performance tracks for technical review. Please follow the instructions below carefully ⬇️

Track Submission Guidelines:
• Send the final track only
• File name must be your performer name
(Example: sarthak_chavan.mp3)
• Format: MP3 or WAV only
• Track should be properly mixed, edited, and cut
• Audio quality should be clear and performance-ready

📩 Mail your tracks to:
sarthakchavan223@gmail.com

These tracks will be checked for quality, timing, and technical feasibility, so please double-check everything before sending.

Thanks for your cooperation, and all the best 💪
If you have any doubts, feel free to reach out."""
