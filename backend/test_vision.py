import asyncio
import base64
from services.ollama_client import analyze_image

async def test():
    print("🚀 Starting Test...")
    
    # Create a simple 1x1 black pixel PNG
    # Base64 for a 1x1 black pixel
    dummy_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    dummy_bytes = base64.b64decode(dummy_image_b64)
    
    print("📸 Sending dummy image to Vision Model...")
    try:
        result = await analyze_image(dummy_bytes)
        print("✅ Result:", result)
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
