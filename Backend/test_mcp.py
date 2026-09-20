import asyncio
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

# Add the Backend folder to sys.path so we can import from app
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "Backend")))

# pyrefly: ignore [missing-import]
from app.services.mcp_client import mcp_client

async def test():
    print("Testing MCP Client Connection...")
    result = await mcp_client.connect()
    print("Connect Result:")
    print(result)

    if result.get("connected"):
        print("\nTesting search_files...")
        try:
            files = await mcp_client.search_files(query="", page_size=5)
            print(f"Found {len(files)} files.")
            for f in files:
                print(f"- {f.get('name')} ({f.get('id')})")
        except Exception as e:
            print(f"Error searching files: {e}")
    else:
        print("\nSkipping search test because connection failed.")

if __name__ == "__main__":
    asyncio.run(test())
