"""
Server-Sent Events (SSE) protocol implementation for MCP.

This module implements the MCP protocol using SSE communication.
SSE is ideal for web-based deployments and Kubernetes environments.
"""

import logging
import sys
import os
from typing import List

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    Tool,
    TextContent,
)

from .base import MCPProtocol
from app.core import URLFetcher, HTMLToMarkdownConverter

logger = logging.getLogger(__name__)


class SseProtocol(MCPProtocol):
    """MCP protocol implementation using Server-Sent Events (SSE)."""
    
    def __init__(self, server_name: str = "mcp-fetcher-http", server_version: str = "1.0.0", 
                 host: str = "localhost", port: int = 8000, endpoint: str = "/messages"):
        """Initialize the SSE protocol.
        
        Args:
            server_name: Name of the MCP server
            server_version: Version of the server
            host: Host to bind the server to
            port: Port to bind the server to
            endpoint: SSE endpoint path for message posting
        """
        super().__init__(server_name, server_version)
        self.host = host
        self.port = port
        self.endpoint = endpoint
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
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool execution requests."""
            return await self.handle_tool_call(request)
    
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
    
    async def handle_tool_call(self, request: CallToolRequest) -> CallToolResult:
        """Handle a tool call request.
        
        Args:
            request: The tool call request
            
        Returns:
            Result of the tool execution
        """
        if request.params.name == "fetch_url":
            url = request.params.arguments.get("url") if request.params.arguments else None
            
            if not url:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: URL parameter is required")]
                )
            
            try:
                # Fetch the HTML content
                html_content = await self.fetcher.fetch_content(str(url))
                
                # Convert to Markdown
                markdown_content = self.converter.convert(html_content)
                
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
                content=[TextContent(type="text", text=f"Unknown tool: {request.params.name}")]
            )
    
    async def run(self) -> None:
        """Run the SSE protocol server."""
        logger.info(f"Starting MCP SSE server on {self.host}:{self.port}")
        logger.info(f"SSE endpoint: {self.endpoint}")
        logger.info("Send Ctrl+C to stop the server")
        
        # Create SSE transport
        transport = SseServerTransport(endpoint=self.endpoint)
        
        # Run the server with SSE transport
        import uvicorn
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import Response
        from starlette.requests import Request
        
        # Create Starlette app for SSE server
        async def handle_sse(request: Request):
            """Handle SSE connections."""
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.app.run(
                    streams[0], streams[1], 
                    InitializationOptions(
                        server_name=self.server_name,
                        server_version=self.server_version,
                        capabilities=self.app.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    )
                )
            # Return empty response to avoid NoneType error
            return Response()
        
        async def health_check(request):
            """Health check endpoint."""
            return Response("OK", status_code=200)
        
        # Create routes
        routes = [
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount(self.endpoint, app=transport.handle_post_message),
            Route("/health", health_check, methods=["GET"]),
        ]
        
        app = Starlette(routes=routes)
        
        # Run with uvicorn
        config = uvicorn.Config(
            app=app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()