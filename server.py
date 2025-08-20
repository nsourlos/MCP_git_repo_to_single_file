"""
MCP Git Files Server - A Model Context Protocol server for processing git repositories and files.
Combines git repository cloning with files-to-prompt functionality.
"""

from fastmcp import FastMCP
import os
import subprocess
import sys
from typing import Optional, List, Dict
import tempfile
import shutil
import re
import hashlib
import logging
from pathlib import Path

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

def clone_repo(repo_url: str) -> str:
    """Clone a repository and return the path. If repository is already cloned in temp directory, reuse it."""
    # Create a deterministic directory name based on repo URL
    repo_hash = hashlib.sha256(repo_url.encode()).hexdigest()[:12]
    temp_dir = os.path.join(tempfile.gettempdir(), f"git_files_server_{repo_hash}")
    
    # If directory exists and is a valid git repo, return it
    if os.path.exists(temp_dir):
        try:
            # Simple check if it's a git repository
            git_dir = os.path.join(temp_dir, '.git')
            if os.path.exists(git_dir):
                logging.info(f"Reusing existing repository at {temp_dir}")
                return temp_dir
        except Exception:
            # If there's any error with existing repo, clean it up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Create directory and clone repository
    os.makedirs(temp_dir, exist_ok=True)
    try:
        logging.info(f"Cloning {repo_url} to {temp_dir}...")
        result = subprocess.run(
            ["git", "clone", repo_url, temp_dir],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"Successfully cloned to {temp_dir}")
        return temp_dir
    except subprocess.CalledProcessError as e:
        # Clean up on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f"Failed to clone repository {repo_url}: {e.stderr}")
    except Exception as e:
        # Clean up on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f"Error cloning repository: {str(e)}")

# def get_directory_tree(path: str, prefix: str = "") -> str:
#     """Generate a tree-like directory structure string"""
#     output = ""
#     try:
#         entries = sorted([e for e in os.listdir(path) if not e.startswith('.git')])
#     except PermissionError:
#         return f"{prefix}[Permission Denied]\n"
    
#     for i, entry in enumerate(entries):
#         is_last = i == len(entries) - 1
#         current_prefix = "└── " if is_last else "├── "
#         next_prefix = "    " if is_last else "│   "
        
#         entry_path = os.path.join(path, entry)
#         output += prefix + current_prefix + entry + "\n"
        
#         if os.path.isdir(entry_path):
#             output += get_directory_tree(entry_path, prefix + next_prefix)
            
#     return output

# @mcp.tool()
# def git_directory_structure(repo_url: str) -> str:
#     """
#     Clone a Git repository and return its directory structure in a tree format.
    
#     Args:
#         repo_url: The URL of the Git repository
        
#     Returns:
#         A string representation of the repository's directory structure
#     """
#     try:
#         # Clone the repository
#         repo_path = clone_repo(repo_url)
        
#         # Generate the directory tree
#         tree = get_directory_tree(repo_path)
#         return tree
            
#     except Exception as e:
#         return f"Error: {str(e)}"

# @mcp.tool()
# def git_read_files(repo_url: str, file_paths: List[str]) -> Dict[str, str]:
#     """
#     Read the contents of specified files in a given git repository.
    
#     Args:
#         repo_url: The URL of the Git repository
#         file_paths: List of file paths to read (relative to repository root)
        
#     Returns:
#         A dictionary mapping file paths to their contents
#     """
#     try:
#         # Clone the repository
#         repo_path = clone_repo(repo_url)
#         results = {}
        
#         for file_path in file_paths:
#             full_path = os.path.join(repo_path, file_path)
            
#             # Check if file exists
#             if not os.path.isfile(full_path):
#                 results[file_path] = f"Error: File not found"
#                 continue
                
#             try:
#                 with open(full_path, 'r', encoding='utf-8') as f:
#                     results[file_path] = f.read()
#             except Exception as e:
#                 results[file_path] = f"Error reading file: {str(e)}"
        
#         return results
            
#     except Exception as e:
#         return {"error": f"Failed to process repository: {str(e)}"} 

@mcp.tool()
def files_to_prompt(
    paths: List[str], 
    extensions: Optional[List[str]] = None,
    include_hidden: bool = False,
    ignore_patterns: Optional[List[str]] = None,
    ignore_files_only: bool = False,
    ignore_gitignore: bool = False,
    output_format: str = "default",  # "default", "cxml", "markdown"
    include_line_numbers: bool = False,
    # max_file_size: int = 1000000,  # 1MB limit per file
    output_file: Optional[str] = None
) -> str:
    """
    Concatenate files into a single prompt for use with LLMs.
    Supports local paths and git repository URLs.
    
    Args:
        paths: List of file/directory paths or git repository URLs to process
        extensions: Only include files with these extensions (e.g., ["py", "txt"])
        include_hidden: Include hidden files and directories
        ignore_patterns: Patterns to ignore (supports wildcards)
        ignore_files_only: Only ignore files, not directories matching patterns
        ignore_gitignore: Ignore .gitignore rules
        output_format: Output format - "default", "cxml", or "markdown"
        include_line_numbers: Include line numbers in output
        # max_file_size: Maximum file size to process (in bytes)
        output_file: If provided, save the output to this file path.
    """
    return _files_to_prompt_internal(
        paths=paths,
        extensions=extensions,
        include_hidden=include_hidden,
        ignore_patterns=ignore_patterns,
        ignore_files_only=ignore_files_only,
        ignore_gitignore=ignore_gitignore,
        output_format=output_format,
        include_line_numbers=include_line_numbers,
        # max_file_size=max_file_size,
        output_file=output_file
    )

def _files_to_prompt_internal(
    paths: List[str], 
    extensions: Optional[List[str]] = None,
    include_hidden: bool = False,
    ignore_patterns: Optional[List[str]] = None,
    ignore_files_only: bool = False,
    ignore_gitignore: bool = False,
    output_format: str = "default",
    include_line_numbers: bool = False,
    # max_file_size: int = 1000000,
    output_file: Optional[str] = None
) -> str:
    """Internal function for files_to_prompt logic"""
    processed_paths = []
    temp_dirs = []
    
    try:
        # Process each path - clone if it's a git URL, otherwise use as-is
        for path in paths:
            logging.info(f"Processing path: {path}")
            if is_git_url(path):
                cloned_path = clone_repo(path)
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
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=300
        )
        
        if result.returncode != 0:
            logging.error(f"Command failed with return code {result.returncode}")
            logging.error(f"stderr: {result.stderr}")
            return f"Error: {result.stderr}"
        
        if output_file:
            # The tool handles file writing. If it printed anything to stdout, log it.
            if result.stdout:
                logging.info(f"Tool output: {result.stdout}")
            logging.info(f"Output successfully saved to {output_file}")
            return result.stdout
        else:
            return result.stdout
        
    except subprocess.TimeoutExpired:
        logging.error("Command timed out after 5 minutes.")
        return "Error: The 'files-to-prompt' command timed out."
    except Exception as e:
        logging.error(f"Error running files-to-prompt: {str(e)}")
        return f"Error running files-to-prompt: {str(e)}"

@mcp.tool()
def git_files_to_prompt(
    repo_url: str,
    extensions: Optional[List[str]] = None,
    include_hidden: bool = False,
    ignore_patterns: Optional[List[str]] = None,
    output_format: str = "markdown",
    include_line_numbers: bool = False,
    output_file: Optional[str] = None
) -> str:
    """
    Clone a git repository and convert its files to a prompt format.
    This is a convenience function that combines git cloning with files-to-prompt.
    
    Args:
        repo_url: The URL of the Git repository
        extensions: Only include files with these extensions (e.g., ["py", "txt"])
        include_hidden: Include hidden files and directories
        ignore_patterns: Patterns to ignore (supports wildcards)
        output_format: Output format - "default", "cxml", or "markdown"
        include_line_numbers: Include line numbers in output
        output_file: If provided, save the output to this file path.
        
    Returns:
        A string containing the formatted content of the repository files
    """
    return _files_to_prompt_internal(
        paths=[repo_url],
        extensions=extensions,
        include_hidden=include_hidden,
        ignore_patterns=ignore_patterns,
        output_format=output_format,
        include_line_numbers=include_line_numbers,
        output_file=output_file
    )

# def main():
    # """Entry point for the MCP server"""
    # mcp.run()

def main():
    """Entry point for the MCP server"""
    import sys
    
    # Check if running as MCP server (no arguments) or with git repo argument
    if len(sys.argv) > 1:
        # Running with git repo argument - process the repo
        repo_url = sys.argv[1]
        logging.info(f"Processing repository: {repo_url}")
        
        # You can add logic here to process the repo directly
        # For example, run files_to_prompt on the repo
        try:
            result = _files_to_prompt_internal(
                paths=[repo_url],
                output_format="txt"
            )
            # print(result)
            logging.info(f"Output length: {len(str(result))} characters")
        except Exception as e:
            print(f"Error processing repository: {e}")
            sys.exit(1)
    else:
        # Running as MCP server
        mcp.run()


if __name__ == "__main__":
    main()
