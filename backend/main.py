from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schemas import ExtractionResponse, Participant
from pydantic import BaseModel

# Service Imports
from services.vision.local_vision import LocalVisionService
from services.messaging.local_whatsapp import LocalMessageService

app = FastAPI(title="VisionNode Backend", version="1.0")

# Service Initialization (Dependencies)
vision_service = LocalVisionService()
message_service = LocalMessageService()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "system": "VisionNode"}

@app.post("/upload", response_model=ExtractionResponse)
async def upload_sheet(file: UploadFile = File(...)):
    """
    Uploads an image, processes it with Vision Service, and returns participants.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    
    # Process with Vision Service
    try:
        raw_data = await vision_service.analyze_image(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision Service Error: {str(e)}")
    
    # Validate and return
    participants = []
    for item in raw_data:
        p = Participant(
            name=item.get("name", "Unknown"),
            phone=str(item.get("phone", "")),
            act=item.get("act", item.get("performance", "Unknown")),
            status=item.get("status", "pending")
        )
        participants.append(p)
        
    return ExtractionResponse(participants=participants)

class InviteRequest(BaseModel):
    participants: List[Participant]

@app.post("/invite")
async def send_invites(request: InviteRequest):
    """
    Triggers the messaging service to send invites.
    """
    print(f"📨 Received invite request for {len(request.participants)} participants")
    
    # Convert Pydantic models to Dicts for the service
    # We use model_dump(by_alias=True) to handle any field aliases if needed
    participants_data = [p.dict(by_alias=True) for p in request.participants]
    
    try:
        # Pass dicts to the service (it modifies them in-place with status)
        stats = await message_service.send_batch(participants_data)
        print(f"✅ Service finished. Stats: {stats}")
        
        return {"status": "completed", "results": participants_data, "stats": stats}
    except Exception as e:
        print(f"🔥 Critical Error in Messaging Service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

