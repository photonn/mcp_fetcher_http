"""Base protocol interface for MCP communication."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from mcp.types import TextContent, Tool


class MCPProtocol(ABC):
    """Abstract base class for MCP protocol implementations."""
    
    def __init__(self, server_name: str, server_version: str = "1.0.0"):
        """Initialize the protocol.
        
        Args:
            server_name: Name of the MCP server
            server_version: Version of the server
        """
        self.server_name = server_name
        self.server_version = server_version
    
    @abstractmethod
    async def run(self) -> None:
        """Run the protocol server.
        
        This method should start the server and handle incoming requests
        according to the specific protocol implementation.
        """
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[Tool]:
        """Get the list of available tools.
        
        Returns:
            List of Tool objects representing available functionality
        """
        pass
    
    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle a tool call request."""
        pass