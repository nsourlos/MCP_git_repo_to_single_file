#!/usr/bin/env python3
"""
Test client for the MCP Git Files Server
"""

import asyncio
from fastmcp import Client

async def test_git_files_server():
    """Test the git files server functionality"""
    
    # Connect to the new server
    client = Client("server.py")
    repo_url = "https://github.com/adhikasp/mcp-git-ingest"
    
    async with client:
        print("🔍 Testing Git Files Server...")
        
        # Test: General files_to_prompt with git URL
        print("\n🔄 Testing files_to_prompt with git URL...")
        try:
            result = await client.call_tool("files_to_prompt", {
                "paths": [repo_url],
                # "extensions": ["md", "py"],
                "output_format": "markdown",
                "output_file": "mcp_git_ingest_output.txt"
            })
            print("✅ General files_to_prompt with git URL successful")
            print(f"Output length: {len(str(result))} characters")
        except Exception as e:
            print(f"❌ Error: {e}")
            return

if __name__ == "__main__":
    asyncio.run(test_git_files_server())