#!/usr/bin/env python3
"""Full end-to-end test of the MCP HTTP Fetcher server.

This script starts the MCP server using the stdio protocol, lists the
available tools as a regular client would, invokes the ``fetch_url`` tool
with a sample URL, and prints the returned Markdown to the console.

Pass a URL as the first argument to fetch a custom page (defaults to
https://www.example.com).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import types
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def run_full_test(url: str) -> None:
    """Run the MCP client flow against the local stdio server."""

    project_root = Path(__file__).resolve().parent
    server_script = project_root / "app" / "server.py"

    if not server_script.exists():
        raise FileNotFoundError(f"Server script not found at {server_script}")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_script), "--protocol", "stdio"],
        cwd=str(project_root),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session and announce the connected server.
            init_result = await session.initialize()
            server_info = init_result.serverInfo
            print(f"Connected to MCP server: {server_info.name} v{server_info.version}")

            # List the available tools exposed by the server.
            tools_result = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            # Call the fetch_url tool with the provided URL.
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


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.example.com"
    try:
        asyncio.run(run_full_test(url))
    except KeyboardInterrupt:
        print("Test interrupted by user.")


if __name__ == "__main__":
    main()
