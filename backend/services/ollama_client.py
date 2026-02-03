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
        max_size = 800 # Reduced to 800 for speed
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
    
    # STRICT System Prompt
    system_prompt = (
        "You are a strict OCR assistant. Read the audition sheet image precisely. "
        "Focus on the 'NAME' and 'CONTACT NO' columns. "
        "Rules:\n"
        "1. VISUAL READ ONLY: Do not invent names. Only output names visible in the image.\n"
        "2. STACKED NAMES: If a single 'NAME' box contains multiple names (one above the other), treat them as SEPARATE participants.\n"
        "3. SHARED PHONES: If they share a 'CONTACT NO' box, assign that number to BOTH names.\n"
        "4. Output JSON Array of objects: [{'name': '...', 'phone': '...', 'act': '...'}].\n"
        "5. 'act' should be the text in 'SONGS' or 'TYPE' column.\n"
        "6. If a cell says 'DUET', assign 'Duet' as the act for both participants.\n"
        "\n"
        "Example of formatting (Generic):\n"
        '[{"name": "Name from Line 1", "phone": "9876543210", "act": "Singing"}, {"name": "Name from Line 2", "phone": "9876543210", "act": "Singing"}]\n'
        "ONLY return the JSON Array."
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
        "stream": True, # Streaming prevents ReadTimeout
        "options": {
            "temperature": 0.0 # Force deterministic output
        }
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client: # 5 min timeout
        try:
            print(f"Sending request to Ollama ({MODEL_NAME})...")
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"--- New Scan Request (Stream) ---\n")
            
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

            # Robust Regex Extraction (Find the largest JSON-like array or object)
            import re
            # Look for [...] or {...}
            json_match = re.search(r'(\[.*\]|\{.*\})', content, re.DOTALL)
            
            if json_match:
                clean_content = json_match.group(0)
            else:
                clean_content = content.replace("```json", "").replace("```", "").strip()

            # Parse the content as JSON
            try:
                data = json.loads(clean_content)
                
                # Normalize Data Structure
                if isinstance(data, dict):
                    # Handle wrapper keys like "auditionSheet", "participants", "data"
                    for key in ["participants", "auditionSheet", "data", "people"]:
                        if key in data and isinstance(data[key], list):
                            data = data[key]
                            break
                    else:
                         # If no known key, maybe the dict itself is a single participant?
                         # Only if it has name/phone
                         if "name" in data:
                             data = [data]
                         else:
                             # Fallback: try to see if values are the list
                             for val in data.values():
                                 if isinstance(val, list):
                                     data = val
                                     break
                
                # Final check: Must be a list of dicts
                if isinstance(data, list):
                    valid_items = []
                    for item in data:
                        if isinstance(item, dict):
                             # Normalize keys (handle upper case or different names)
                             normalized = {}
                             for k, v in item.items():
                                 k_lower = k.lower()
                                 if "name" in k_lower: normalized["name"] = v
                                 elif "contact" in k_lower or "phone" in k_lower: normalized["phone"] = v
                                 elif "act" in k_lower or "song" in k_lower or "type" in k_lower: normalized["act"] = v
                             
                             if "name" in normalized:
                                 valid_items.append({
                                     "name": normalized["name"],
                                     "phone": str(normalized.get("phone", "0000000000")).replace(" ", "").replace("-", ""),
                                     "act": normalized.get("act", "Unknown")
                                 })
                            
                        elif isinstance(item, str):
                            # Fallback: The model might have put the table in a string
                            # Try to parse row by row from the string
                            print(f"⚠️ attempting to parse string row: {item}")
                            import re
                            # Simple heuristics for "Name Phone Act" or "| Name | Phone | Act |"
                            # We look for a phone number pattern
                            phone_match = re.search(r'(\d[\d\s-]{9,})', item)
                            if phone_match:
                                phone = phone_match.group(1).strip()
                                # Assume Text before phone is name, text after is act
                                parts = item.split(phone)
                                name = parts[0].replace("|", "").strip()
                                act = parts[1].replace("|", "").strip() if len(parts) > 1 else "Unknown"
                                
                                # Clean up
                                if len(name) > 2:
                                    valid_items.append({
                                        "name": name,
                                        "phone": phone.replace(" ", "").replace("-", ""),
                                        "act": act
                                    })

                    if not valid_items:
                        # Return empty list if parsing yielded nothing, handled by frontend?
                        # Or better, return a "Scan Failed" row so user knows it ran but failed
                        pass 
                    
                    return valid_items
                    
                return []
            except json.JSONDecodeError:
                error_msg = f"Failed to parse JSON: {content}"
                print(error_msg)
                with open("debug.log", "a", encoding="utf-8") as f:
                    f.write(f"{error_msg}\n")
                # Failsafe Row
                return [{"name": "Error Reading Image", "phone": "0000000000", "act": "Please Enter Manually", "status": "failed"}]
                
        except Exception as e:
            error_msg = f"Ollama Error: {repr(e)}"
            print(error_msg)
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"{error_msg}\n")
            # Failsafe Row
            return [{"name": "Scan Timeout/Error", "phone": "0000000000", "act": "Please Enter Manually", "status": "failed"}]
