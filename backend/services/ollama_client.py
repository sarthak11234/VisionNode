import httpx
import json
import base64
from typing import List, Dict, Any
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL_NAME = "llava"

async def analyze_image(image_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Sends image to Ollama for analysis and returns structured JSON data.
    """
    
    # Resize image if too large (prevents Ollama 500 OOM errors)
    try:
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_bytes))
        max_size = 1280 # Increased for legibility (800 was too blurry)
        if img.width > max_size or img.height > max_size:
            print(f"Resizing image from {img.width}x{img.height} to max {max_size}px...")
            img.thumbnail((max_size, max_size))
            
            # Convert back to bytes
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            image_bytes = buf.getvalue()
    except Exception as e:
        print(f"Image resize warning: {e}")

    # Encode image to base64
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # RAW OCR System Prompt (No JSON)
    system_prompt = (
        "Read the text in this image line by line. "
        "Output EXACTLY what you see. "
        "Do not interpret or format the data. "
        "Do not invent names or numbers. "
        "Just output the raw text content."
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
        "stream": True, 
        "options": {
            "temperature": 0.0 # Force deterministic output
        }
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client: 
        try:
            print(f"Sending request to Ollama ({MODEL_NAME})...")
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"--- New Scan Request (Raw OCR) ---\n")
            
            content = ""
            async with client.stream("POST", f"{OLLAMA_HOST}/api/chat", json=payload) as response:
                 response.raise_for_status()
                 async for chunk in response.aiter_lines():
                     if chunk:
                         try:
                             json_chunk = json.loads(chunk)
                             part = json_chunk.get("message", {}).get("content", "")
                             content += part
                             print(part, end="", flush=True)
                         except:
                             pass

            print(f"\nFull Streamed Response: {content}") 
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"Raw Response: {content}\n")

            # --- RAW TEXT PARSING ---
            valid_items = []
            import re
            
            # Regex to find phone numbers (common Indian formats)
            # Matches: 9876543210, +91 98765 43210, 987-654-3210
            phone_pattern = re.compile(r'(?:(?:\+|0){0,2}91(\s*[\-]\s*)?|[0]?)?[6789]\d{9}')
            
            lines = content.split('\n')
            
            # Context buffer for lines that might be names standing alone
            name_buffer = []
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Check for phone number
                phone_match = phone_pattern.search(line.replace(" ", "").replace("-", ""))
                
                if phone_match:
                    raw_phone = phone_match.group(0)
                    # Locate phone in original string to split name/act
                    # Since we stripped spaces in match, this is tricky. 
                    # Simpler approach: find the digit sequence in the original line
                    
                    # Find sequence of digits that constitute the phone
                    digit_match = re.search(r'\d[\d\s-]{9,}', line)
                    
                    name = "Unknown"
                    act = "Unknown"
                    phone = raw_phone
                    
                    if digit_match:
                        phone_str = digit_match.group(0)
                        parts = line.split(phone_str)
                        
                        # LEFT of phone is usually Name
                        if len(parts) > 0:
                            potential_name = parts[0].strip(" |,-:").strip()
                            if len(potential_name) > 2:
                                name = potential_name
                            elif name_buffer:
                                # If line starts with phone, maybe name was on previous line
                                name = " ".join(name_buffer)
                                name_buffer = [] # consumed
                        
                        # RIGHT of phone is usually Act/Song
                        if len(parts) > 1:
                            potential_act = parts[1].strip(" |,-:").strip()
                            if len(potential_act) > 2:
                                act = potential_act
                    
                    # If we found a name in the buffer but no phone on that line, 
                    # and now we found a phone, we pair them.
                    
                    valid_items.append({
                        "name": name,
                        "phone": phone.replace(" ", "").replace("-", "")[-10:], # Keep last 10 digits
                        "act": act,
                        "status": "pending"
                    })
                    name_buffer = [] # Reset buffer after match
                    
                else:
                    # No phone number found. 
                    # Might be a name on its own line (mismatched row).
                    # Or header/junk.
                    # Heuristic: If it has letters and is short-ish, keep in buffer
                    if len(line) > 2 and len(line) < 50 and not "name" in line.lower() and not "contact" in line.lower():
                        name_buffer.append(line)
                        # Keep max 1 line in buffer to avoid merging headers
                        if len(name_buffer) > 1: 
                            name_buffer.pop(0)

            if not valid_items:
                 return [{"name": "No Data Found", "phone": "", "act": "Check Image", "status": "failed"}]

            return valid_items
                
        except Exception as e:
            error_msg = f"Ollama Error: {repr(e)}"
            print(error_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{error_msg}\n")
            # Failsafe Row
            return [{"name": "Scan Failed", "phone": "", "act": "Manual Entry Required", "status": "failed"}]
