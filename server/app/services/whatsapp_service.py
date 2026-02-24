import logging
import httpx
import time
import random
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        # The base URL for the WAHA server from docker-compose
        self.base_url = settings.WAHA_BASE_URL
        self.session_name = "default"

    def _apply_jitter_delay(self, message_body: str):
        """
        Implementation of the Jitter-Delay Algorithm to prevent Meta from banning the burner number.
        Delay = (word_count / 4) + random_jitter(2, 5) seconds to simulate human typing.
        """
        word_count = len(message_body.split())
        base_delay = word_count / 4.0
        jitter = random.uniform(2.0, 5.0)
        total_delay = base_delay + jitter
        
        logger.info(f"Applying jitter delay of {total_delay:.2f}s for humanizing.")
        time.sleep(total_delay)

    def send_freeform_message(self, to_number: str, body: str):
        """
        Sends a freeform text message via WAHA HTTP API.
        This entirely replaces the need for Twilio templates.
        """
        # Ensure the phone number suffix conforms to WAHA format
        # WAHA expects `1234567890@c.us` or just the international number depending on version, 
        # but typically `<number>@c.us` works best.
        formatted_to = to_number
        if not formatted_to.endswith("@c.us"):
            formatted_to = f"{formatted_to}@c.us"
            
        # Strip `+` if present as WAHA usually prefers just the digits
        formatted_to = formatted_to.replace("+", "")

        # Apply humanizing delay
        self._apply_jitter_delay(body)

        try:
            with httpx.Client() as client:
                payload = {
                    "chatId": formatted_to,
                    "text": body,
                    "session": self.session_name
                }
                # WAHA endpoint for sending text
                response = client.post(f"{self.base_url}/api/sendText", json=payload, timeout=10.0)
                response.raise_for_status()
                
                logger.info(f"WhatsApp message sent to {formatted_to} via WAHA")
                return response.json().get("id", "waha_success_id")
                
        except httpx.ConnectError:
            logger.error(f"Failed to connect to WAHA at {self.base_url}. Is the docker container running?")
            raise
        except Exception as e:
            logger.error(f"Failed to send WAHA WhatsApp message: {str(e)}")
            raise e

whatsapp_service = WhatsAppService()
