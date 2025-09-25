#!/usr/bin/env python3
"""
MCP HTTP Fetcher Server

A Model Context Protocol (MCP) server that fetches web pages and converts them to Markdown.
This server exposes a single tool that accepts a URL, downloads the page content,
and returns it converted to Markdown format.
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.protocols.stdio import StdioProtocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-fetcher-http")


async def main():
    """Main entry point for the server."""
    protocol = StdioProtocol()
    await protocol.run()


if __name__ == "__main__":
    asyncio.run(main())