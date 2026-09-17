import asyncio
import os
import json
import base64
from dotenv import load_dotenv

# Load env variables including any PAT or keys
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.services.mcp_client import mcp_client

async def test_github_mcp():
    print("\n[GitHub MCP Test] Starting live test...\n")
    
    # We can pass a personal access token if we have one in env,
    # otherwise public GitHub API endpoints still work (with lower rate limits).
    # Since OAuth gives us access tokens for users, we'll simulate a request here.
    token = os.getenv("GITHUB_PAT") or None # Optional: user can add GITHUB_PAT to .env for higher rate limits
    
    try:
        # Test: Get File Content
        print("2. Testing 'github_get_file_content' (Fetching README.md from tiangolo/fastapi)...")
        file_result = await mcp_client.call_tool(
            "github_get_file_content",
            {
                "owner": "tiangolo",
                "repo": "fastapi",
                "path": "README.md"
            },
            token=token
        )
        
        file_content = file_result.get("content", [])
        if file_content:
            base64_data = file_content[0].get("text", "")
            decoded = base64.b64decode(base64_data).decode("utf-8")
            print(f"   Success! Fetched file. Preview of content:\n")
            print("-" * 50)
            print(decoded[:250] + "...\n")
            print("-" * 50)
            
    except Exception as e:
        print(f"\n[Error] Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_github_mcp())
