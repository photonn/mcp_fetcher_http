# MCP HTTP Fetcher Server

A Model Context Protocol (MCP) server that fetches web pages and converts them to Markdown format. This server supports both **SSE (Server-Sent Events)** and **Stdio** protocols, making it suitable for web deployments, Kubernetes environments, desktop clients, and sidecar patterns.

## Features

- ✅ **Dual Protocol Support**: SSE (default) and Stdio protocols
- ✅ **HTTP/HTTPS URL fetching**: Download content from any web URL
- ✅ **HTML to Markdown conversion**: Clean conversion using html2text
- ✅ **MCP Protocol compliance**: Follows MCP server standards
- ✅ **Kubernetes ready**: SSE protocol with health checks and graceful scaling
- ✅ **Sidecar friendly**: Stdio protocol for process-to-process communication
- ✅ **Error handling**: Robust error handling for network issues
- ✅ **Docker support**: Ready-to-run Docker container
- ✅ **Async operation**: Non-blocking HTTP requests
- ✅ **Modular architecture**: Clean separation of concerns for maintainability

## Quick Start

### SSE Protocol (Default - Web/Kubernetes Deployments)
```bash
# Start with SSE protocol (default)
python app/server.py

# Custom host/port for Kubernetes
python app/server.py --protocol sse --host 0.0.0.0 --port 8000
```

### Stdio Protocol (Desktop Clients/Sidecars)
```bash
# Start with stdio protocol
python app/server.py --protocol stdio
```

## Protocol Overview

| Protocol | Use Case | Deployment | Scaling |
|----------|----------|------------|---------|
| **SSE (Default)** | Web apps, APIs, Kubernetes | HTTP server with endpoints | Horizontal scaling, load balancing |
| **Stdio** | Desktop clients, sidecars | Process communication | Single client per process |

For detailed protocol documentation, see [docs/PROTOCOLS.md](docs/PROTOCOLS.md).

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
│   │   ├── stdio.py       # Standard I/O protocol implementation
│   │   └── sse.py         # Server-Sent Events protocol implementation
│   └── server.py          # New modular server entry point
├── docs/                  # Documentation
│   └── PROTOCOLS.md       # Comprehensive protocol guide
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

- **`python app/server.py`** - Primary entry point with full protocol support
- **`python server.py`** - Legacy entry point (limited protocol options)
- **`./run_server.sh`** - Convenience script with dependency management

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
# SSE protocol (default - for web/Kubernetes deployments)
python app/server.py

# Stdio protocol (for desktop clients)
python app/server.py --protocol stdio

# Custom SSE configuration
python app/server.py --protocol sse --host 0.0.0.0 --port 8080

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
# SSE protocol (default)
docker run -p 8000:8000 mcp-fetcher-http

# Stdio protocol
docker run -it mcp-fetcher-http python app/server.py --protocol stdio
```

**Note:** Docker build may require internet access to install Python packages. In restricted environments, use the direct Python installation method.

## Usage

The server exposes a single MCP tool called `fetch_url` that accepts a URL parameter and returns the page content converted to Markdown.

### MCP Client Configuration

#### For SSE Protocol (Web/Kubernetes deployments)
```json
{
  "mcpServers": {
    "http-fetcher": {
      "command": "curl",
      "args": ["-N", "-H", "Accept: text/event-stream", "http://localhost:8000/sse"],
      "description": "HTTP fetcher using SSE protocol"
    }
  }
}
```

#### For Stdio Protocol (Desktop clients)
```json
{
  "mcpServers": {
    "http-fetcher": {
      "command": "python",
      "args": ["/path/to/mcp_fetcher_http/app/server.py", "--protocol", "stdio"],
      "description": "HTTP fetcher using stdio protocol"
    }
  }
}
```

### Command Line Options

```bash
python app/server.py --help
```

Available options:
- `--protocol {stdio,sse}` - Communication protocol (default: sse)
- `--host HOST` - Host to bind SSE server (default: localhost)
- `--port PORT` - Port for SSE server (default: 8000)  
- `--endpoint ENDPOINT` - SSE message endpoint (default: /messages)
- `--server-name NAME` - Server identifier
- `--server-version VERSION` - Server version

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
