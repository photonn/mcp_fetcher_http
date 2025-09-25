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

# Allow choice of entry point (backward compatible by default)
if [ "$1" = "--new" ]; then
    echo "Running new modular MCP server..."
    python app/server.py
else
    echo "Running MCP server (backward compatible mode)..."
    echo "Use './run_server.sh --new' to use the new modular structure"
    python server.py
fi