# MCP HTTP Fetcher Server - Protocol Guide

This document provides comprehensive information about running the MCP HTTP Fetcher Server with both supported communication protocols.

## Supported Protocols

The server supports two MCP communication protocols:

1. **SSE (Server-Sent Events)** - *Default and recommended*
2. **Stdio (Standard Input/Output)** - For desktop clients and sidecars

## Protocol Selection

### Default Behavior
By default, the server runs in SSE mode:
```bash
# These are equivalent
python app/server.py
python app/server.py --protocol sse
```

### Explicit Protocol Selection
```bash
# SSE protocol (web-based, Kubernetes-friendly)
python app/server.py --protocol sse

# Stdio protocol (desktop clients, sidecars)
python app/server.py --protocol stdio
```

## SSE (Server-Sent Events) Protocol

### Overview
SSE is the default and recommended protocol for most deployments. It provides:
- HTTP-based communication
- Web-friendly architecture
- Easy integration with load balancers
- Natural fit for Kubernetes deployments
- Built-in health check endpoints

### Basic Usage
```bash
# Start SSE server on default port (8000)
python app/server.py --protocol sse

# Start on custom host/port
python app/server.py --protocol sse --host 0.0.0.0 --port 8080

# Start with custom message endpoint
python app/server.py --protocol sse --endpoint /api/messages
```

### Server Endpoints
When running in SSE mode, the server exposes:
- `/sse` - SSE connection endpoint for MCP clients
- `/messages` - POST endpoint for sending messages (configurable with --endpoint)
- `/health` - Health check endpoint

### Configuration Options
```bash
python app/server.py --protocol sse \
  --host 0.0.0.0 \           # Bind to all interfaces
  --port 8000 \              # Port number
  --endpoint /messages \     # Message POST endpoint
  --server-name my-server \  # Server identifier
  --server-version 2.0.0     # Server version
```

## Stdio Protocol

### Overview
Stdio protocol is ideal for:
- Desktop MCP clients (like Claude Desktop)
- Sidecar containers
- Process-to-process communication
- Testing and development

### Basic Usage
```bash
# Start stdio server
python app/server.py --protocol stdio
```

### Configuration Options
```bash
python app/server.py --protocol stdio \
  --server-name my-server \  # Server identifier
  --server-version 2.0.0     # Server version
```

Note: Host and port options are ignored in stdio mode.

## Kubernetes Deployment

### SSE Protocol with Kubernetes

SSE protocol is ideal for Kubernetes deployments. Here's a complete example:

#### Deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-fetcher-http
  labels:
    app: mcp-fetcher-http
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-fetcher-http
  template:
    metadata:
      labels:
        app: mcp-fetcher-http
    spec:
      containers:
      - name: mcp-fetcher-http
        image: mcp-fetcher-http:latest
        ports:
        - containerPort: 8000
          name: http
        command:
          - python
          - app/server.py
          - --protocol
          - sse
          - --host
          - "0.0.0.0"
          - --port
          - "8000"
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-fetcher-http-service
spec:
  selector:
    app: mcp-fetcher-http
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-fetcher-http-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
spec:
  rules:
  - host: mcp-fetcher.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-fetcher-http-service
            port:
              number: 80
```

#### ConfigMap for Custom Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-fetcher-config
data:
  server-name: "mcp-fetcher-k8s"
  server-version: "1.0.0"
  endpoint: "/api/messages"
---
# Update deployment to use ConfigMap
spec:
  template:
    spec:
      containers:
      - name: mcp-fetcher-http
        # ... other configuration ...
        command:
          - python
          - app/server.py
          - --protocol
          - sse
          - --host
          - "0.0.0.0"
          - --port
          - "8000"
          - --server-name
          - "$(SERVER_NAME)"
          - --server-version
          - "$(SERVER_VERSION)"
          - --endpoint
          - "$(ENDPOINT)"
        envFrom:
        - configMapRef:
            name: mcp-fetcher-config
```

### Helm Chart Example
```yaml
# values.yaml
replicaCount: 3

image:
  repository: mcp-fetcher-http
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
  hosts:
    - host: mcp-fetcher.example.com
      paths:
        - path: /
          pathType: Prefix

config:
  protocol: sse
  host: "0.0.0.0"
  port: 8000
  serverName: "mcp-fetcher-k8s"
  serverVersion: "1.0.0"
  endpoint: "/messages"

resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi"
    cpu: "100m"

healthCheck:
  enabled: true
  path: /health
```

## Sidecar Deployment

### Stdio Protocol as Sidecar

The stdio protocol is perfect for sidecar patterns:

#### Kubernetes Sidecar Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: main-app-with-mcp-sidecar
spec:
  replicas: 1
  selector:
    matchLabels:
      app: main-app
  template:
    metadata:
      labels:
        app: main-app
    spec:
      containers:
      # Main application container
      - name: main-app
        image: main-app:latest
        ports:
        - containerPort: 3000
        volumeMounts:
        - name: shared-socket
          mountPath: /shared
        
      # MCP Fetcher sidecar
      - name: mcp-fetcher-sidecar
        image: mcp-fetcher-http:latest
        command:
          - python
          - app/server.py
          - --protocol
          - stdio
          - --server-name
          - "mcp-fetcher-sidecar"
        stdin: true
        tty: true
        volumeMounts:
        - name: shared-socket
          mountPath: /shared
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "50m"
      
      volumes:
      - name: shared-socket
        emptyDir: {}
```

#### Docker Compose Sidecar Example
```yaml
version: '3.8'
services:
  main-app:
    image: main-app:latest
    ports:
      - "3000:3000"
    depends_on:
      - mcp-fetcher-sidecar
    volumes:
      - shared:/shared
    
  mcp-fetcher-sidecar:
    image: mcp-fetcher-http:latest
    command:
      - python
      - app/server.py
      - --protocol
      - stdio
      - --server-name
      - mcp-fetcher-sidecar
    stdin_open: true
    tty: true
    volumes:
      - shared:/shared

volumes:
  shared:
```

## Client Configuration

### MCP Client Configuration for SSE
```json
{
  "mcpServers": {
    "http-fetcher-sse": {
      "command": "curl",
      "args": [
        "-N",
        "-H", "Accept: text/event-stream",
        "http://localhost:8000/sse"
      ],
      "description": "HTTP fetcher using SSE protocol"
    }
  }
}
```

### MCP Client Configuration for Stdio
```json
{
  "mcpServers": {
    "http-fetcher-stdio": {
      "command": "python",
      "args": ["/path/to/mcp_fetcher_http/app/server.py", "--protocol", "stdio"],
      "description": "HTTP fetcher using stdio protocol"
    }
  }
}
```

## Testing and Development

### Testing SSE Protocol
```bash
# Start server
python app/server.py --protocol sse --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test SSE endpoint (in another terminal)
curl -N -H "Accept: text/event-stream" http://localhost:8000/sse
```

### Testing Stdio Protocol
```bash
# Start server
python app/server.py --protocol stdio

# Server will wait for input on stdin
# Test with sample JSON-RPC message:
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python app/server.py --protocol stdio
```

## Performance Considerations

### SSE Protocol
- **Throughput**: Higher throughput for multiple concurrent clients
- **Scalability**: Easily scalable with load balancers
- **Resource Usage**: Slightly higher memory usage per connection
- **Latency**: Network latency dependent

### Stdio Protocol
- **Throughput**: Lower overhead for single client
- **Scalability**: Limited to single client per process
- **Resource Usage**: Lower memory footprint
- **Latency**: Minimal latency (direct process communication)

## Security Considerations

### SSE Protocol
- Exposed HTTP endpoints require network security
- Use HTTPS in production
- Implement authentication/authorization as needed
- DNS rebinding protection is built-in

### Stdio Protocol
- Process-level security
- No network exposure
- Inherits security context of parent process

## Troubleshooting

### Common SSE Issues
```bash
# Check if server is running
curl http://localhost:8000/health

# Check server logs
python app/server.py --protocol sse 2>&1 | tee server.log

# Test with verbose output
python app/server.py --protocol sse --host 0.0.0.0 --port 8000
```

### Common Stdio Issues
```bash
# Test stdio protocol directly
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python app/server.py --protocol stdio

# Debug with logging
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import asyncio
from app.protocols.stdio import StdioProtocol
asyncio.run(StdioProtocol().run())
"
```

## Migration Guide

### From Stdio to SSE
1. Update deployment configuration to use SSE protocol
2. Change client configuration to use HTTP endpoints
3. Update monitoring to use health check endpoints
4. Consider load balancing for high availability

### From SSE to Stdio
1. Update deployment to single-process model
2. Change client configuration to use stdio
3. Update process management for restart handling