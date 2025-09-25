"""
Standard input/output protocol implementation for MCP.

This module implements the MCP protocol using stdin/stdout communication.
"""

import logging
import sys
import os
from typing import Any, Dict, List

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .base import MCPProtocol
from app.core import URLFetcher, HTMLToMarkdownConverter

logger = logging.getLogger(__name__)


class StdioProtocol(MCPProtocol):
    """MCP protocol implementation using standard input/output."""
    
    def __init__(self, server_name: str = "mcp-fetcher-http", server_version: str = "1.0.0"):
        """Initialize the stdio protocol.
        
        Args:
            server_name: Name of the MCP server
            server_version: Version of the server
        """
        super().__init__(server_name, server_version)
        self.app = Server(server_name)
        self.fetcher = URLFetcher()
        self.converter = HTMLToMarkdownConverter()
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""
        
        @self.app.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return self.get_available_tools()
        
        @self.app.call_tool()
        async def handle_call_tool(tool_name: str, arguments: Dict[str, Any] | None):
            """Handle tool execution requests."""
            return await self.handle_tool_call(tool_name, arguments or {})
    
    def get_available_tools(self) -> List[Tool]:
        """Get the list of available tools.
        
        Returns:
            List of Tool objects representing available functionality
        """
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
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle a tool call request."""

        if name != "fetch_url":
            raise ValueError(f"Unknown tool: {name}")

        url = arguments.get("url")
        if not url:
            raise ValueError("URL parameter is required")

        try:
            html_content = await self.fetcher.fetch_content(str(url))
            markdown_content = self.converter.convert(html_content)
            return [TextContent(type="text", text=markdown_content)]
        except Exception as exc:
            error_message = f"Error fetching URL: {exc}"
            logger.error(error_message)
            raise RuntimeError(error_message) from exc
    
    async def run(self) -> None:
        """Run the stdio protocol server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.server_name,
                    server_version=self.server_version,
                    capabilities=self.app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )