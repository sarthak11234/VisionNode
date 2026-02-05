from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IVisionService(ABC):
    @abstractmethod
    async def analyze_image(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Analyze an image and return a list of participants.
        Returns: List of dicts with keys: name, phone, act
        """
        pass

class IMessagingService(ABC):
    @abstractmethod
    async def send_invite(self, phone: str, message: str) -> bool:
        """
        Send a single message to a phone number.
        """
        pass
    
    @abstractmethod
    async def send_batch(self, participants: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Send messages to a list of participants.
        Returns: Dict with counts for 'sent' and 'failed'.
        """
        pass
