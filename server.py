"""
MCP Git Files Server - A Model Context Protocol server for processing git repositories and files.
Combines git repository cloning with files-to-prompt functionality.
"""

from fastmcp import FastMCP
import os
import subprocess
import sys
from typing import Optional, List
import shutil
import re
import hashlib
import logging
import asyncio
import anyio
import git

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')

mcp = FastMCP(
    "Git Files-to-Prompt Server",
    dependencies=[
        "gitpython==3.1.45",
        "files-to-prompt==0.6"
    ]
)

def is_git_url(path: str) -> bool:
    """Check if a path is a git repository URL"""
    git_patterns = [
        r'^https?://github\.com/',
        r'^https?://gitlab\.com/',
        r'^https?://bitbucket\.org/',
        r'^git@github\.com:',
        r'^git@gitlab\.com:',
        r'^git@bitbucket\.org:',
        r'\.git$'
    ]
    return any(re.match(pattern, path) for pattern in git_patterns)

async def clone_repo(repo_url: str) -> str:
    """Clone a repository and return the path. If repository is already cloned in current directory, reuse it."""
    # Create a deterministic directory name based on repo URL
    repo_hash = hashlib.sha256(repo_url.encode()).hexdigest()[:12]
    current_dir = os.getcwd()
    repo_dir = os.path.join(current_dir, f"git_files_server_{repo_hash}")
    
    # If directory exists and is a valid git repo, return it
    if os.path.exists(repo_dir):
        try:
            # Simple check if it's a git repository
            git_dir = os.path.join(repo_dir, '.git')
            if os.path.exists(git_dir):
                logging.info(f"Reusing existing repository at {repo_dir}")
                return repo_dir
        except Exception:
            # If there's any error with existing repo, clean it up
            shutil.rmtree(repo_dir, ignore_errors=True)
    
    # Create directory and clone repository
    os.makedirs(repo_dir, exist_ok=True)
    try:
        logging.info(f"Cloning {repo_url} to {repo_dir}...")

        def _clone_repo():
            repo = git.Repo.clone_from(repo_url, repo_dir)
            return repo
        
        result = await anyio.to_thread.run_sync(_clone_repo)
        logging.info(f"Cloned repository: {result}")
        return repo_dir

    except Exception as e:
        # Clean up on error
        shutil.rmtree(repo_dir, ignore_errors=True)
        raise Exception(f"Error cloning repository: {str(e)}")

@mcp.tool()
async def files_to_prompt(
    paths: List[str], 
    extensions: List[str] = [],  
    include_hidden: bool = False,
    ignore_patterns: List[str] = [], 
    ignore_files_only: bool = False,
    ignore_gitignore: bool = False,
    output_format: str = "default",
    include_line_numbers: bool = False,
    output_file: str = "" 
) -> str:
    """
    Concatenate files into a single prompt for use with LLMs.
    Supports local paths and git repository URLs.
    
    Args:
        paths: List of file/directory paths or git repository URLs to process
        extensions: Only include files with these extensions (e.g., ["py", "txt"]). Empty list means all files.
        include_hidden: Include hidden files and directories
        ignore_patterns: Patterns to ignore (supports wildcards). Empty list means no patterns.
        ignore_files_only: Only ignore files, not directories matching patterns
        ignore_gitignore: Ignore .gitignore rules
        output_format: Output format - "default", "cxml", or "markdown"
        include_line_numbers: Include line numbers in output
        output_file: If provided, save the output to this file path. Empty string means no file output.
    """
    logging.info(f"files_to_prompt paths: {paths}")
    # Convert empty lists/strings to None for internal function
    extensions_param = extensions if extensions else None
    ignore_patterns_param = ignore_patterns if ignore_patterns else None
    output_file_param = output_file if output_file else None
    
    return await _files_to_prompt_internal(
        paths=paths,
        extensions=extensions_param,
        include_hidden=include_hidden,
        ignore_patterns=ignore_patterns_param,
        ignore_files_only=ignore_files_only,
        ignore_gitignore=ignore_gitignore,
        output_format=output_format,
        include_line_numbers=include_line_numbers,
        output_file=output_file_param
    )

async def _files_to_prompt_internal(
    paths: List[str], 
    extensions: Optional[List[str]] = None,
    include_hidden: bool = False,
    ignore_patterns: Optional[List[str]] = None,
    ignore_files_only: bool = False,
    ignore_gitignore: bool = False,
    output_format: str = "default",
    include_line_numbers: bool = False,
    output_file: Optional[str] = None
) -> str:
    
    """Internal function for files_to_prompt logic"""

    logging.info(f"files_to_prompt_internal paths: {paths}")
    processed_paths = []
    temp_dirs = []
    
    try:
        # Process each path - clone if it's a git URL, otherwise use as-is
        for path in paths:
            logging.info(f"Processing path: {path}")
            if is_git_url(path):
                cloned_path = await clone_repo(path)
                processed_paths.append(cloned_path)
                temp_dirs.append(cloned_path)
            else:
                processed_paths.append(path)
        
        # Build command for files-to-prompt
        cmd = ["files-to-prompt"]
        cmd.extend(processed_paths)
        
        # Add options
        if extensions:
            for ext in extensions:
                cmd.extend(["-e", ext])
        
        if include_hidden:
            cmd.append("--include-hidden")
        
        if ignore_patterns:
            for pattern in ignore_patterns:
                cmd.extend(["--ignore", pattern])
        
        if ignore_files_only:
            cmd.append("--ignore-files-only")
        
        if ignore_gitignore:
            cmd.append("--ignore-gitignore")
        
        if output_format == "cxml":
            cmd.append("--cxml")
        elif output_format == "markdown":
            cmd.append("--markdown")
        
        if include_line_numbers:
            cmd.append("--line-numbers")
        
        if output_file:
            cmd.extend(["-o", output_file])
        
        # Execute the command
        logging.info(f"Executing command: {' '.join(cmd)}")

        def _run_f2p():
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                stdin=subprocess.DEVNULL
            )

        result = await anyio.to_thread.run_sync(_run_f2p)

        if result.returncode != 0:
            logging.error(f"Command failed with return code {result.returncode}")
            logging.error(f"stderr: {result.stderr}")
            raise Exception(f"Failed to run files-to-prompt: {result.stderr}")
        
        if output_file:
            logging.error(f"No output was written to {output_file}")
            return result.stdout #f"Error: No output was written to {output_file}"
        else:
            return result.stdout
       
    except Exception as e:
        logging.error(f"Error running files-to-prompt: {str(e)}")
        return f"Error running files-to-prompt: {str(e)}"

def main():
    """Entry point for the MCP server"""
    import sys

    args = sys.argv[1:]
    
    # Check if running as MCP server (no arguments) or with git repo argument
    if not args or args[0].startswith("-"):
        logging.info("Running as MCP server")
        mcp.run()
        return
    
    repo_url = args[0]
    async def process_repo():
        logging.info(f"Processing repository: {repo_url}")
        try:
            result = await _files_to_prompt_internal(
                paths=[repo_url],
                output_format="markdown",
                # output_file="mcp_test_output.txt"
            )
            logging.info(f"Output length: {len(str(result))} characters")
        except Exception as e:
            print(f"Error processing repository: {e}")
            sys.exit(1)
    
    asyncio.run(process_repo())

if __name__ == "__main__":
    main()