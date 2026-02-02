from pydantic import BaseModel, Field
from typing import List, Optional

class Participant(BaseModel):
    name: str = Field(..., description="Name of the participant")
    phone: str = Field(..., description="10-digit phone number of the participant")
    act: str = Field(..., description="Type of performance or act")
    confidence: Optional[float] = Field(None, description="Confidence score if available")

class ExtractionResponse(BaseModel):
    participants: List[Participant]
