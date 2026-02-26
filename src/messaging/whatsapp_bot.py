import re
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

# Base delay constraint parameters for "leaky bucket" rate limiting
MIN_WAIT_SECONDS = 10
MAX_WAIT_SECONDS = 20

def format_e164(phone_number: str) -> str:
    """
    Sanitizes phone numbers into E.164 format.
    Input example: "+91 987-654-3210" -> Output: "919876543210"
    """
    # Remove all non-numeric characters
    sanitized = re.sub(r'\D', '', phone_number)
    return sanitized

class WhatsAppBot:
    def __init__(self, session_dir: str):
        self.session_dir = session_dir
        self.driver = None

    def start_session(self, visible: bool = False):
        """
        Initializes the Chrome WebDriver.
        Mounts the user data directory to persist the WhatsApp login session.
        """
        options = webdriver.ChromeOptions()
        
        # Pointing to the persistent session directory
        options.add_argument(f"user-data-dir={os.path.abspath(self.session_dir)}")
        
        if not visible:
            options.add_argument("--headless=new")
            
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        
        # Attempt to launch driver
        logger.info(f"Starting Chrome WebDriver (Visible: {visible})")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://web.whatsapp.com")
        
        try:
            # Wait for the main page to load, indicating successful login
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "side"))
            )
            logger.info("Successfully loaded WhatsApp Web.")
        except TimeoutException:
            logger.warning("Timeout waiting for WhatsApp to load. Please scan the QR code if running in visible mode.")

    def close(self):
        if self.driver:
            self.driver.quit()

    def send_message(self, phone_number: str, message: str) -> bool:
        """
        Sends a WhatsApp message via the Web UI to a given E.164 phone number.
        Includes rate limiting to avoid triggering spam filters.
        """
        if not self.driver:
            raise RuntimeError("WebDriver is not initialized. Call start_session() first.")
            
        formatted_number = format_e164(phone_number)
        encoded_message = message.replace('\n', '%0A')
        
        # Navigate directly to the chat link
        api_link = f"https://web.whatsapp.com/send?phone={formatted_number}&text={encoded_message}"
        self.driver.get(api_link)
        
        try:
            # Wait for send button to become clickable
            send_btn = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
            )
            time.sleep(1) # Brief human jitter
            send_btn.click()
            
            logger.info(f"Message sent to {formatted_number}")
            
            import random
            # Leaky Bucket Rate Limiting (10 to 20 seconds)
            sleep_time = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
            logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds before next message...")
            time.sleep(sleep_time)
            
            return True
            
        except TimeoutException:
            logger.error(f"Failed to send message to {formatted_number}: Timeout while waiting for send button.")
            return False
        except Exception as e:
            logger.error(f"Error sending message to {formatted_number}: {str(e)}")
            return False
