#!/usr/bin/env python3
"""End-to-end test client for the MCP HTTP Fetcher SSE server."""

from __future__ import annotations

import argparse
import asyncio
from typing import Tuple

from mcp import types
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


async def run_sse_test(url: str, host: str, port: int) -> None:
    """Run the MCP client flow against an SSE server."""

    base_url = f"http://{host}:{port}"
    sse_url = f"{base_url}/sse"

    print(f"Connecting to MCP SSE server at {sse_url}")

    async with sse_client(sse_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            init_result = await session.initialize()
            server_info = init_result.serverInfo
            print(f"Connected to MCP server: {server_info.name} v{server_info.version}")

            tools_result = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\nRequesting Markdown for:", url)
            tool_result = await session.call_tool("fetch_url", {"url": url})

            if tool_result.isError:
                print("The server reported an error while fetching the URL.")
                for item in tool_result.content:
                    print(item)
                return

            print("\nMarkdown output:\n" + "=" * 80)
            for item in tool_result.content:
                if isinstance(item, types.TextContent):
                    print(item.text)
                else:
                    print(f"[Unsupported content returned: {item}]")
            print("=" * 80)


def parse_args() -> Tuple[str, str, int]:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Test the MCP HTTP Fetcher SSE server by fetching a URL.",
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://www.example.com",
        help="The URL to fetch and convert to Markdown.",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host where the MCP SSE server is running (default: localhost).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port where the MCP SSE server is running (default: 8000).",
    )

    args = parser.parse_args()
    return args.url, args.host, args.port


def main() -> None:
    url, host, port = parse_args()
    try:
        asyncio.run(run_sse_test(url, host, port))
    except KeyboardInterrupt:
        print("Test interrupted by user.")


if __name__ == "__main__":
    main()
