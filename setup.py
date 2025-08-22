#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-git-files-server",
    version="0.1.0",
    author="nsourlos",
    author_email="your.email@example.com",
    description="A Model Context Protocol server for processing git repositories and files (optimized for uv)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-git-files-server",
    py_modules=["server"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastmcp==2.11.3",
        "gitpython==3.1.45",
        "files-to-prompt==0.6"
    ],
    entry_points={
        "console_scripts": [
            "mcp-git-files-server=server:main",
        ],
    },
)