import httpx
import json
import base64
from typing import List, Dict, Any
import os
import re
from PIL import Image
import io
from ..interfaces import IVisionService

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL_NAME = "llava"

class LocalVisionService(IVisionService):
    async def analyze_image(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Sends image to local Ollama instance for analysis and returns extracted participants.
        """
        # 1. Resize image if too large
        try:
            img = Image.open(io.BytesIO(image_bytes))
            max_size = 1280 
            if img.width > max_size or img.height > max_size:
                print(f"Resizing image from {img.width}x{img.height} to max {max_size}px...")
                img.thumbnail((max_size, max_size))
                
                # Convert back to bytes
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                image_bytes = buf.getvalue()
        except Exception as e:
            print(f"Image resize warning: {e}")

        # 2. Encode image
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # 3. Prepare Prompt (Raw OCR)
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
            "options": {"temperature": 0.0}
        }
        
        # 4. Send Request (Streaming)
        async with httpx.AsyncClient(timeout=300.0) as client: 
            try:
                print(f"Sending request to Ollama ({MODEL_NAME})...")
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

                # 5. Parse Raw Text
                return self._parse_raw_text(content)
                    
            except Exception as e:
                error_msg = f"Ollama Error: {repr(e)}"
                print(error_msg)
                return [{"name": "Scan Failed", "phone": "", "act": "Manual Entry Required", "status": "failed"}]

    def _parse_raw_text(self, text: str) -> List[Dict[str, Any]]:
        valid_items = []
        # Regex to find phone numbers (common Indian formats)
        phone_pattern = re.compile(r'(?:(?:\+|0){0,2}91(\s*[\-]\s*)?|[0]?)?[6789]\d{9}')
        
        lines = text.split('\n')
        name_buffer = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Check for phone number
            phone_match = phone_pattern.search(line.replace(" ", "").replace("-", ""))
            
            if phone_match:
                raw_phone = phone_match.group(0)
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
                            name = " ".join(name_buffer)
                            name_buffer = [] # consumed
                    
                    # RIGHT of phone is usually Act/Song
                    if len(parts) > 1:
                        potential_act = parts[1].strip(" |,-:").strip()
                        if len(potential_act) > 2:
                            act = potential_act
                
                valid_items.append({
                    "name": name,
                    "phone": phone.replace(" ", "").replace("-", "")[-10:], 
                    "act": act,
                    "status": "pending"
                })
                name_buffer = [] 
                
            else:
                if len(line) > 2 and len(line) < 50 and not "name" in line.lower() and not "contact" in line.lower():
                    name_buffer.append(line)
                    if len(name_buffer) > 1: 
                        name_buffer.pop(0)

        if not valid_items:
             return [{"name": "No Data Found", "phone": "", "act": "Check Image", "status": "failed"}]

        return valid_items
