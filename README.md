# MCP HTTP Fetcher Server

A simple Model Context Protocol (MCP) server that fetches web pages and converts them to Markdown format. This server allows connecting applications to send URLs and receive the page content converted to clean, readable Markdown.

## Features

- ✅ **HTTP/HTTPS URL fetching**: Download content from any web URL
- ✅ **HTML to Markdown conversion**: Clean conversion using html2text
- ✅ **MCP Protocol compliance**: Follows MCP server standards
- ✅ **Error handling**: Robust error handling for network issues
- ✅ **Docker support**: Ready-to-run Docker container
- ✅ **Async operation**: Non-blocking HTTP requests
- ✅ **Modular architecture**: Clean separation of concerns for maintainability
- ✅ **Protocol extensibility**: Abstract interface for future protocol implementations

## Project Structure

The project follows Python best practices with a clean, modular architecture:

```
mcp_fetcher_http/
├── app/                    # Main application package
│   ├── core/              # Core business logic
│   │   ├── fetcher.py     # URL fetching functionality
│   │   └── converter.py   # HTML to Markdown conversion
│   ├── protocols/         # Protocol implementations
│   │   ├── base.py        # Abstract protocol interface
│   │   └── stdio.py       # Standard I/O protocol implementation
│   └── server.py          # New modular server entry point
├── tests/                 # Test suite
│   ├── test_fetcher.py    # Tests for URL fetching
│   ├── test_converter.py  # Tests for HTML conversion
│   └── test_server.py     # Integration tests
├── examples/              # Example usage and demos
│   ├── demo.py           # Functionality demonstration
│   └── mcp_config_example.json
├── server.py             # Backward-compatible entry point
├── requirements.txt      # Python dependencies
└── Dockerfile           # Container configuration
```

### Entry Points

- **`python server.py`** - Backward-compatible entry point (recommended for existing setups)
- **`python app/server.py`** - New modular entry point (recommended for new installations)
- **`./run_server.sh`** - Convenience script with dependency management
- **`./run_server.sh --new`** - Convenience script using new modular structure

## Installation

### Option 1: Direct Python Installation

1. Clone the repository:
```bash
git clone https://github.com/photonn/mcp_fetcher_http.git
cd mcp_fetcher_http
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python server.py
# OR use the convenience script:
./run_server.sh
```

### Option 2: Docker Installation

1. Build the Docker image:
```bash
docker build -t mcp-fetcher-http .
```

2. Run the container:
```bash
docker run -it mcp-fetcher-http
```

**Note:** Docker build may require internet access to install Python packages. In restricted environments, use the direct Python installation method.

## Usage

The server exposes a single MCP tool called `fetch_url` that accepts a URL parameter and returns the page content converted to Markdown.

### MCP Client Configuration

Add the server to your MCP client configuration (example for Claude Desktop):

```json
{
  "mcpServers": {
    "http-fetcher": {
      "command": "python",
      "args": ["/path/to/mcp_fetcher_http/server.py"],
      "description": "HTTP fetcher that converts web pages to Markdown"
    }
  }
}
```

For new installations using the modular structure:
```json
{
  "mcpServers": {
    "http-fetcher": {
      "command": "python",
      "args": ["/path/to/mcp_fetcher_http/app/server.py"],
      "description": "HTTP fetcher that converts web pages to Markdown (modular version)"
    }
  }
}
```

### Tool Schema

```json
{
  "name": "fetch_url",
  "description": "Fetch a web page and convert it to Markdown format",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "The URL of the web page to fetch and convert to Markdown"
      }
    },
    "required": ["url"]
  }
}
```

### Example Usage

When connected to an MCP client, you can use the tool like this:

```json
{
  "name": "fetch_url",
  "arguments": {
    "url": "https://example.com"
  }
}
```

The server will return the page content converted to Markdown format.

## Testing

Run the included test scripts to verify functionality:

```bash
# Run all tests (recommended)
python tests/test_server.py      # Integration tests
python tests/test_fetcher.py     # URL fetching tests  
python tests/test_converter.py   # HTML conversion tests

# Run demo to see HTML to Markdown conversion
python examples/demo.py
```

### Testing the MCP Server

The server communicates via stdin/stdout using the MCP protocol. For basic testing:

1. Start the server: `python server.py` (or `python app/server.py`)
2. The server will wait for MCP protocol messages on stdin
3. Send a list_tools request to see available tools
4. Send a call_tool request with the fetch_url tool

For easier testing, use an MCP client like Claude Desktop or develop a simple test client.

## Configuration

The server includes the following configurable aspects:

- **Timeout**: 30-second timeout for HTTP requests
- **Content types**: Accepts HTML and XML content types
- **Markdown conversion**: Preserves links and images in output

## Error Handling

The server handles various error conditions:

- Invalid URLs
- Network connectivity issues
- HTTP error responses (4xx, 5xx)
- Content parsing errors
- Timeout conditions

## Security Considerations

- The server validates URLs before processing
- Runs in a non-root Docker container
- Has reasonable timeout limits to prevent hanging
- Does not execute or process JavaScript content

## Dependencies

- `mcp>=1.0.0` - Model Context Protocol server framework
- `aiohttp>=3.9.0` - Async HTTP client for fetching URLs
- `html2text>=2020.1.16` - HTML to Markdown conversion
- `typing-extensions>=4.0.0` - Type hints support

## License

Licensed under the Apache License, Version 2.0. See the LICENSE file for details.
