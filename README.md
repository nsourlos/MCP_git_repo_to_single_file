# MCP GitHub Files Server

A Model Context Protocol (MCP) server that clones a GitHub repository and uses [files-to-prompt](https://github.com/simonw/files-to-prompt) to convert it to a single LLM file. This server allows you to:

- Analyze GitHub repository directory structures
- Read all files  
- Convert GitHub repositories to prompt format using files-to-prompt

## Features

- **GitHub Repository Analysis**: Clone and analyze the structure of any public GitHub repository
- **File Reading**: Read files from GitHub repositories
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

> **Note**: This MCP server may have compatibility issues on Visual Studio Code. It has been tested on macOS and Windows 10. To test if the server is installed correctly, run 
`python test_client.py`

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


1. Create a `C:\Users\<user>\AppData\Roaming\Code\User\mcp.json` (if in Windows) file and a `.vscode/mcp.json` file in your project root, both with the following content:
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
<!-- uvx looks for an executable or entry point named mcp-git-files-server and runs it -->

2. Open the [MCP SERVERS - INSTALLED](https://code.visualstudio.com/assets/docs/copilot/chat/mcp-servers/extensions-view-mcp-servers.png) section in the Extensions view and ```Start Server```. Run the ```MCP: List Servers``` command from the Command Palette (```Command+Shift+P```) to view the list of installed MCP servers

## Tools

### files_to_prompt
Convert files and directories to LLM prompt format. Supports both local paths and git URLs.

**Parameters:**
- `paths` (List[str]): List of file/directory paths or git repository URLs
- `extensions` (List[str]): Only include files with these extensions (default: [])
- `include_hidden` (bool): Include hidden files and directories (default: False)
- `ignore_patterns` (List[str]): Patterns to ignore (default: [])
- `ignore_files_only` (bool): Only ignore files, not directories matching patterns (default: False)
- `ignore_gitignore` (bool): Ignore .gitignore rules (default: False)
- `output_format` (str): Output format - "default", "cxml", or "markdown" (default: "default")
- `include_line_numbers` (bool): Include line numbers in output (default: False)
- `output_file` (str): Output file path (default: "")

**Example:**
```python
files_to_prompt(
    paths=["https://github.com/user/repo"],
    extensions=["py", "md"],
    output_format="markdown"
)
```

## Key Improvements

This implementation provides several key advantages:

1. **Cross-Editor Compatibility**: Works with both Cursor (native MCP) and VS Code (possibly issues due to non-native MCP support)
2. **No Local Setup**: Users don't need to install dependencies manually. Dependencies declared in `pyproject.toml` and installed automatically
3. **Version Control**: Server code is version controlled and can be updated via git
4. **Consistent Environment** and **Reliable Installation**: Dependencies are managed consistently with uv
5. **Better Performance**: Smart caching reduces repeated git operations, uv provides faster installs
6. **Easy Distribution**: Can be shared via GitHub URL

<!-- ## License

MIT License -->