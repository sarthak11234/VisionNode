import httpx
import json
import base64
from typing import List, Dict, Any
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "llava"

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
            print(f"Sending request to Ollama ({MODEL_NAME})...")
            response = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("message", {}).get("content", "[]")
            
            # Write to log file for guaranteed visibility
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- NEW REQUEST ---\nRaw Ollama Response: {content}\n")

            print(f"Raw Ollama Response: {content}") 

            # Robust Regex Extraction
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
            if json_match:
                clean_content = json_match.group(0)
            else:
                clean_content = content.strip() # Fallback

            # Parse the content as JSON
            try:
                data = json.loads(clean_content)
                # Ensure it's a list
                if isinstance(data, dict):
                    # Sometimes models return a wrapper object like {"participants": [...]}
                    if "participants" in data:
                        return data["participants"]
                    return [data]
                return data
            except json.JSONDecodeError:
                error_msg = f"Failed to parse JSON: {content}"
                print(error_msg)
                with open("debug.log", "a", encoding="utf-8") as f:
                    f.write(f"{error_msg}\n")
                return []
                
        except Exception as e:
            error_msg = f"Ollama Error: {str(e)}"
            print(error_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{error_msg}\n")
            return []
