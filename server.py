#!/usr/bin/env python3
"""
MCP HTTP Fetcher Server

A Model Context Protocol (MCP) server that fetches web pages and converts them to Markdown.
This server exposes a single tool that accepts a URL, downloads the page content,
and returns it converted to Markdown format.
"""

import asyncio
import logging
from typing import Any, Sequence
from urllib.parse import urlparse
import aiohttp
import html2text
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-fetcher-http")

# Create the MCP server instance
app = Server("mcp-fetcher-http")


def is_valid_url(url: str) -> bool:
    """Validate if the provided string is a valid HTTP/HTTPS URL."""
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


async def fetch_and_convert_url(url: str) -> str:
    """
    Fetch a URL and convert its HTML content to Markdown.
    
    Args:
        url: The URL to fetch
        
    Returns:
        Markdown content as string
        
    Raises:
        Exception: If fetching or conversion fails
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL provided: {url}")
    
    # Configure html2text converter
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # Don't wrap lines
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: Failed to fetch {url}")
                
                # Get the content type to ensure it's HTML-like
                content_type = response.headers.get('content-type', '').lower()
                if 'html' not in content_type and 'xml' not in content_type:
                    logger.warning(f"Content type '{content_type}' may not be HTML")
                
                # Read the response content
                html_content = await response.text()
                
                # Convert HTML to Markdown
                markdown_content = h.handle(html_content)
                
                logger.info(f"Successfully converted {url} to Markdown ({len(markdown_content)} characters)")
                return markdown_content
                
    except aiohttp.ClientError as e:
        raise Exception(f"Network error while fetching {url}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing {url}: {str(e)}")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="fetch_url",
            description="Fetch a web page and convert it to Markdown format",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to fetch and convert to Markdown"
                    }
                },
                "required": ["url"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool execution requests."""
    if request.name == "fetch_url":
        url = request.arguments.get("url")
        
        if not url:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: URL parameter is required")]
            )
        
        try:
            markdown_content = await fetch_and_convert_url(str(url))
            return CallToolResult(
                content=[TextContent(type="text", text=markdown_content)]
            )
        except Exception as e:
            error_message = f"Error fetching URL: {str(e)}"
            logger.error(error_message)
            return CallToolResult(
                content=[TextContent(type="text", text=error_message)]
            )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {request.name}")]
        )


async def main():
    """Main entry point for the server."""
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-fetcher-http",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())