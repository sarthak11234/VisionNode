import httpx
import json
import base64
from typing import List, Dict, Any
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "llama3.2-vision"

async def analyze_image(image_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Sends image to Ollama for analysis and returns structured JSON data.
    """
    
    # Encode image to base64
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # STRICT System Prompt
    system_prompt = (
        "You are a professional registrar. Analyze the provided image of an audition sheet. "
        "Output a valid JSON array of objects with keys 'name', 'phone', and 'act'. "
        "Only include 10-digit numbers for 'phone'. If a number is unclear, suffix it with '??'. "
        "Do not include any other text, markdown, or explanation. ONLY the JSON array."
    )
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": system_prompt,
                "images": [b64_image]
            }
        ],
        "stream": False,
        "format": "json" # Force valid JSON response
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("message", {}).get("content", "[]")
            
            # Parse the content as JSON
            try:
                data = json.loads(content)
                # Ensure it's a list
                if isinstance(data, dict):
                    # Sometimes models return a wrapper object like {"participants": [...]}
                    if "participants" in data:
                        return data["participants"]
                    return [data]
                return data
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {content}")
                return []
                
        except Exception as e:
            print(f"Ollama Error: {str(e)}")
            return []
