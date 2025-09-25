#!/bin/bash
# MCP HTTP Fetcher Server Runner Script

# Set up the environment
echo "Starting MCP HTTP Fetcher Server..."
echo "Press Ctrl+C to stop the server"
echo

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# Run the server
echo "Running MCP server (communicates via stdin/stdout)..."
python server.py