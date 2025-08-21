# MCP Git Files Server

A Model Context Protocol (MCP) server that clones a git repository and uses files-to-prompt to convert it to a single LLM file. This server allows you to:

- Analyze git repository directory structures
- Read all files  
- Convert git repositories to prompt format using files-to-prompt
<!-- - Process both local paths and remote git repositories -->

## Features

- **Git Repository Analysis**: Clone and analyze the structure of any public git repository
- **File Reading**: Read files from git repositories
- **Files to Prompt**: Convert files and directories to LLM-friendly prompt format
- **Smart Caching**: Reuses cloned repositories to improve performance
- **Multiple Formats**: Support for Markdown, and CXML output formats

## Prerequisites

This package uses `uv` for fast Python package management. Install `uv` first if you haven't already:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# or on macOS
brew install uv
# or on Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

### From Git (Recommended)

```bash
uv pip install git+https://github.com/nsourlos/MCP_git_repo_to_single_file
```

### Local Development

```bash
git clone https://github.com/nsourlos/MCP_git_repo_to_single_file
cd MCP_git_repo_to_single_file
uv pip install -e .
```

## Configuration

> **Note for Windows Users**: This MCP server may have compatibility issues on Windows systems. It has been primarily tested on macOS. If you encounter issues on Windows, consider using WSL (Windows Subsystem for Linux) for better compatibility.


### Cursor Configuration

Cursor has native MCP support. Add this to your Cursor MCP settings file at `~/.cursor/mcp.json`:

```json
{
    "mcpServers": {
        "git-files-server": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/nsourlos/MCP_git_repo_to_single_file", "mcp-git-files-server"],
            "env": {}
        }
    }
}
```

### VS Code Configuration

VS Code doesn't have native MCP support, but you can use the server through VS Code Tasks for easy access:

#### Option 1: VS Code Tasks (Recommended)

1. Create a `.vscode/mcp.json` file in your project root:
```json

{
    "servers": {
        "git-files-server": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/nsourlos/MCP_git_repo_to_single_file", "mcp-git-files-server"],
            "env": {}
        }
    }
}

```

2. Open the [MCP SERVERS - INSTALLED](https://code.visualstudio.com/assets/docs/copilot/chat/mcp-servers/extensions-view-mcp-servers.png) section in the Extensions view. Run the ```MCP: List Servers``` command from the Command Palette (```Command+Shift+P```) to view the list of installed MCP servers

#### Option 2: Terminal Integration

Simply run commands in VS Code's integrated terminal:

```bash
# Run the server (for testing)
uvx --from git+https://github.com/nsourlos/MCP_git_repo_to_single_file mcp-git-files-server

# Test with the provided client
python test_client.py
```

## Tools

<!-- ### git_directory_structure
Get the directory structure of a git repository in tree format.

**Parameters:**
- `repo_url` (str): The URL of the git repository

**Example:**
```python
git_directory_structure("https://github.com/user/repo")
```

### git_read_files
Read specific files from a git repository.

**Parameters:**
- `repo_url` (str): The URL of the git repository
- `file_paths` (List[str]): List of file paths to read (relative to repo root)

**Example:**
```python
git_read_files("https://github.com/user/repo", ["README.md", "src/main.py"])
``` -->

### files_to_prompt
Convert files and directories to LLM prompt format. Supports both local paths and git URLs.

**Parameters:**
- `paths` (List[str]): List of file/directory paths or git repository URLs
- `extensions` (Optional[List[str]]): Only include files with these extensions
- `include_hidden` (bool): Include hidden files and directories
- `ignore_patterns` (Optional[List[str]]): Patterns to ignore
- `ignore_files_only` (bool): Only ignore files, not directories matching patterns
- `ignore_gitignore` (bool): Ignore .gitignore rules
- `output_format` (str): Output format - "default", "cxml", or "markdown"
- `include_line_numbers` (bool): Include line numbers in output

**Example:**
```python
files_to_prompt(
    paths=["https://github.com/user/repo"],
    extensions=["py", "md"],
    output_format="markdown"
)
```

### git_files_to_prompt
Convenience function that combines git cloning with files-to-prompt.

**Parameters:**
- `repo_url` (str): The URL of the git repository
- `extensions` (Optional[List[str]]): Only include files with these extensions
- `include_hidden` (bool): Include hidden files and directories
- `ignore_patterns` (Optional[List[str]]): Patterns to ignore
- `output_format` (str): Output format - "default", "cxml", or "markdown"
- `include_line_numbers` (bool): Include line numbers in output

**Example:**
```python
git_files_to_prompt(
    repo_url="https://github.com/user/repo",
    extensions=["py"],
    output_format="markdown"
)
```

## Key Improvements

This implementation provides several key advantages:

1. **Cross-Editor Compatibility**: Works with both Cursor (native MCP) and VS Code
2. **No Local Setup**: Users don't need to install dependencies manually. Dependencies declared in `pyproject.toml` and installed automatically
3. **Version Control**: Server code is version controlled and can be updated via git
4. **Consistent Environment**: Dependencies are managed consistently with uv
5. **Better Performance**: Smart caching reduces repeated git operations, uv provides faster installs
6. **Multiple Tools**: Provides both specific and general-purpose tools
7. **Easy Distribution**: Can be shared via GitHub URL
8. **Reliable Installation**: uv provides better dependency resolution than pip


<!-- ## License

MIT License -->
