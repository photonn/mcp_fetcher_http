#!/usr/bin/env python3
"""
MCP HTTP Fetcher Server

A Model Context Protocol (MCP) server that fetches web pages and converts them to Markdown.
This server exposes a single tool that accepts a URL, downloads the page content,
and returns it converted to Markdown format.

Supports both stdio and SSE (Server-Sent Events) protocols:
- stdio: Standard input/output communication (ideal for desktop apps, sidecars)
- sse: HTTP-based Server-Sent Events (ideal for web deployments, Kubernetes)
"""

import argparse
import asyncio
import logging
import sys
import os

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.protocols.stdio import StdioProtocol
from app.protocols.sse import SseProtocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-fetcher-http")


def create_argument_parser():
    """Create argument parser for server options."""
    parser = argparse.ArgumentParser(
        description="MCP HTTP Fetcher Server - Fetch web pages and convert to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Protocol Options:
  stdio: Standard Input/Output (for desktop clients, sidecars)
  sse:   Server-Sent Events over HTTP (for web deployments, Kubernetes)

Examples:
  # Run with SSE protocol (default)
  python app/server.py

  # Run with stdio protocol
  python app/server.py --protocol stdio

  # Run SSE server on custom host/port
  python app/server.py --protocol sse --host 0.0.0.0 --port 8080

  # For Kubernetes deployment
  python app/server.py --protocol sse --host 0.0.0.0 --port 8000
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
    
    parser.add_argument(
        "--endpoint",
        default="/messages",
        help="SSE endpoint path for message posting (default: /messages, ignored for stdio)"
    )
    
    parser.add_argument(
        "--server-name",
        default="mcp-fetcher-http",
        help="Server name identifier (default: mcp-fetcher-http)"
    )
    
    parser.add_argument(
        "--server-version",
        default="1.0.0",
        help="Server version (default: 1.0.0)"
    )
    
    return parser


async def main():
    """Main entry point for the server."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    logger.info(f"Starting MCP Fetcher HTTP Server v{args.server_version}")
    logger.info(f"Protocol: {args.protocol}")
    
    if args.protocol == "stdio":
        logger.info("Using stdio protocol - suitable for desktop clients and sidecars")
        protocol = StdioProtocol(
            server_name=args.server_name,
            server_version=args.server_version
        )
    elif args.protocol == "sse":
        logger.info(f"Using SSE protocol - suitable for web deployments and Kubernetes")
        logger.info(f"Server will bind to {args.host}:{args.port}")
        protocol = SseProtocol(
            server_name=args.server_name,
            server_version=args.server_version,
            host=args.host,
            port=args.port,
            endpoint=args.endpoint
        )
    
    try:
        await protocol.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())