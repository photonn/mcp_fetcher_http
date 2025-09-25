#!/usr/bin/env python3
"""
MCP HTTP Fetcher Server - Main Entry Point

This file maintains backward compatibility while delegating to the new application structure.
For new installations, consider using 'python app/server.py' directly.
"""

import asyncio
import logging
from app.protocols.stdio import StdioProtocol

# Configure logging  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-fetcher-http")

# Re-export core functionality for backward compatibility
from app.core import is_valid_url, URLFetcher, HTMLToMarkdownConverter

# Create convenience function that matches old interface
async def fetch_and_convert_url(url: str) -> str:
    """Fetch a URL and convert its HTML content to Markdown.
    
    This function provides backward compatibility with the old server.py interface.
    
    Args:
        url: The URL to fetch
        
    Returns:
        Markdown content as string
        
    Raises:
        Exception: If fetching or conversion fails
    """
    fetcher = URLFetcher()
    converter = HTMLToMarkdownConverter()
    
    html_content = await fetcher.fetch_content(url)
    return converter.convert(html_content)


async def main():
    """Main entry point for the server."""
    protocol = StdioProtocol()
    await protocol.run()


if __name__ == "__main__":
    asyncio.run(main())