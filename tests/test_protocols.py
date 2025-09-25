#!/usr/bin/env python3
"""
Test both MCP protocols (stdio and SSE) to ensure they work correctly.
"""

import asyncio
import json
import sys
import os
import aiohttp
import time

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.protocols.stdio import StdioProtocol
from app.protocols.sse import SseProtocol


async def test_stdio_protocol():
    """Test stdio protocol functionality."""  
    print("Testing Stdio Protocol...")
    print("=" * 40)
    
    try:
        # Create protocol instance
        protocol = StdioProtocol()
        
        # Test tool listing
        tools = protocol.get_available_tools()
        assert len(tools) > 0, "No tools available"
        assert tools[0].name == "fetch_url", "fetch_url tool not found"
        print("✓ Stdio protocol tools are correctly configured")
        
        # Test tool call with mock data
        from mcp.types import CallToolRequest, CallToolRequestParams
        
        # Test invalid URL
        params = CallToolRequestParams(name="fetch_url", arguments={"url": "invalid-url"})
        request = CallToolRequest(params=params)
        result = await protocol.handle_tool_call(request)
        assert "Error fetching URL" in result.content[0].text
        print("✓ Stdio protocol error handling works")
        
        # Test HTML conversion directly
        sample_html = "<h1>Test</h1><p>Sample content</p>"
        markdown = protocol.converter.convert(sample_html)
        assert "# Test" in markdown
        assert "Sample content" in markdown
        print("✓ Stdio protocol HTML conversion works")
        
        print("✓ Stdio protocol tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Stdio protocol test failed: {e}")
        return False


async def test_sse_protocol():
    """Test SSE protocol functionality."""
    print("\nTesting SSE Protocol...")
    print("=" * 40)
    
    try:
        # Create protocol instance  
        protocol = SseProtocol(host="localhost", port=8001)
        
        # Test tool listing
        tools = protocol.get_available_tools()
        assert len(tools) > 0, "No tools available"
        assert tools[0].name == "fetch_url", "fetch_url tool not found"
        print("✓ SSE protocol tools are correctly configured")
        
        # Test tool call with mock data
        from mcp.types import CallToolRequest, CallToolRequestParams
        
        # Test invalid URL
        params = CallToolRequestParams(name="fetch_url", arguments={"url": "invalid-url"})
        request = CallToolRequest(params=params)
        result = await protocol.handle_tool_call(request)
        assert "Error fetching URL" in result.content[0].text
        print("✓ SSE protocol error handling works")
        
        # Test HTML conversion directly
        sample_html = "<h1>Test</h1><p>Sample content</p>"
        markdown = protocol.converter.convert(sample_html)
        assert "# Test" in markdown
        assert "Sample content" in markdown
        print("✓ SSE protocol HTML conversion works")
        
        print("✓ SSE protocol tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ SSE protocol test failed: {e}")
        return False


async def test_sse_server_startup():
    """Test that SSE server can start up properly."""
    print("\nTesting SSE Server Startup...")
    print("=" * 40)
    
    try:
        # This test just checks that we can create the server without errors
        # We won't actually start it to avoid port conflicts
        protocol = SseProtocol(host="localhost", port=8002)
        
        # Verify server configuration
        assert protocol.host == "localhost"
        assert protocol.port == 8002
        assert protocol.endpoint == "/messages"
        print("✓ SSE server configuration is correct")
        
        # Test we can import required dependencies
        import uvicorn
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import Response
        print("✓ SSE server dependencies are available")
        
        return True
        
    except Exception as e:
        print(f"✗ SSE server startup test failed: {e}")
        return False


async def main():
    """Run all protocol tests."""
    print("Running MCP Protocol Tests...\n")
    
    # Test stdio protocol
    stdio_result = await test_stdio_protocol()
    
    # Test SSE protocol
    sse_result = await test_sse_protocol()
    
    # Test SSE server startup
    sse_startup_result = await test_sse_server_startup()
    
    print("\n" + "=" * 50)
    if stdio_result and sse_result and sse_startup_result:
        print("All protocol tests passed! 🎉")
        return 0
    else:
        print("Some protocol tests failed! ❌")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)