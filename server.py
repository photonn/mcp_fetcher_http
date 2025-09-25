#!/usr/bin/env python3
"""
MCP HTTP Fetcher Server - Main Entry Point

This file maintains backward compatibility while delegating to the new application structure.
For new installations, consider using 'python app/server.py' directly.

Supports both stdio and SSE protocols with SSE as default.
"""

import argparse
import asyncio
import logging
from app.protocols.stdio import StdioProtocol
from app.protocols.sse import SseProtocol

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


def create_argument_parser():
    """Create argument parser for server options."""
    parser = argparse.ArgumentParser(
        description="MCP HTTP Fetcher Server (Legacy Entry Point)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Protocol Options:
  stdio: Standard Input/Output (for desktop clients, sidecars)
  sse:   Server-Sent Events over HTTP (for web deployments, Kubernetes)

Examples:
  # Run with SSE protocol (default)
  python server.py

  # Run with stdio protocol
  python server.py --protocol stdio

  # Run SSE server on custom host/port
  python server.py --protocol sse --host 0.0.0.0 --port 8080

Note: For new installations, use 'python app/server.py' instead.
        """
    )
    
    parser.add_argument(
        "--protocol",
        choices=["stdio", "sse"],
        default="sse",
        help="Communication protocol to use (default: sse)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind SSE server to (default: localhost, ignored for stdio)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind SSE server to (default: 8000, ignored for stdio)"
    )
    
    return parser


async def main():
    """Main entry point for the server."""
    # Check if run without arguments for backward compatibility
    import sys
    if len(sys.argv) == 1:
        logger.info("Running in legacy stdio mode for backward compatibility")
        logger.info("Use --protocol sse to enable SSE mode, or use 'python app/server.py' for full options")
        protocol = StdioProtocol()
    else:
        parser = create_argument_parser()
        args = parser.parse_args()
        
        logger.info(f"Protocol: {args.protocol}")
        
        if args.protocol == "stdio":
            protocol = StdioProtocol()
        elif args.protocol == "sse":
            logger.info(f"SSE server will bind to {args.host}:{args.port}")
            protocol = SseProtocol(host=args.host, port=args.port)
    
    try:
        await protocol.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())