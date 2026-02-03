import httpx
import asyncio
import sys

async def test_connect(url):
    print(f"Testing {url}...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            print(f"✅ Success! Status: {resp.status_code}")
            print(f"Response: {resp.text[:100]}...")
            return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

async def main():
    print("--- Ollama Connectivity Debugger ---")
    
    # Test 1: Localhost
    u1 = "http://localhost:11434/api/tags"
    r1 = await test_connect(u1)
    
    # Test 2: 127.0.0.1
    u2 = "http://127.0.0.1:11434/api/tags"
    r2 = await test_connect(u2)
    
    if r1 or r2:
        print("\n✨ At least one connection worked!")
    else:
        print("\n💀 Both failed. is Ollama running?")

if __name__ == "__main__":
    asyncio.run(main())
