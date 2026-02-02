from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schemas import ExtractionResponse, Participant
from services.ollama_client import analyze_image

app = FastAPI(title="VisionNode Backend", version="1.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
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
    Uploads an image, processes it with Ollama Vision, and returns the extracted participants.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    
    # Process with Ollama
    raw_data = await analyze_image(contents)
    
    # Validate and return
    # We map raw dicts to our Pydantic models
    participants = []
    for item in raw_data:
        # Basic normalization to match our schema keys if the model hallucinates slightly different keys
        p = Participant(
            name=item.get("name", "Unknown"),
            phone=str(item.get("phone", "")),
            act=item.get("act", item.get("performance", "Unknown"))
        )
        participants.append(p)
        
    return ExtractionResponse(participants=participants)
