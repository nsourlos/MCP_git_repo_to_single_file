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
        
        # # Test 1: Get directory structure
        # print("\n📁 Testing git_directory_structure...")
        # try:
        #     result = await client.call_tool("git_directory_structure", {
        #         "repo_url": repo_url
        #     })
        #     print("✅ Directory structure retrieved successfully")
        #     print(f"Preview: {str(result)[:200]}...")
        # except Exception as e:
        #     print(f"❌ Error: {e}")
        
        # # Test 2: Read specific files
        # print("\n📄 Testing git_read_files...")
        # try:
        #     result = await client.call_tool("git_read_files", {
        #         "repo_url": repo_url,
        #         "file_paths": ["README.md", "src/mcp_git_ingest/main.py"]
        #     })
        #     print("✅ Files read successfully")
        #     print(f"Files retrieved: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        # except Exception as e:
        #     print(f"❌ Error: {e}")
        


        # # Test 3: Git files to prompt
        # print("\n🚀 Testing git_files_to_prompt...")
        # try:
        #     result = await client.call_tool("git_files_to_prompt", {
        #         "repo_url": repo_url,
        #         "extensions": ["py"],
        #         "output_format": "markdown"
        #     })
        #     print("✅ Files to prompt conversion successful")
        #     print(f"Output length: {len(str(result))} characters")
        # except Exception as e:
        #     print(f"❌ Error: {e}")
        
        # Test 4: General files_to_prompt with git URL
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

if __name__ == "__main__":
    asyncio.run(test_git_files_server())
