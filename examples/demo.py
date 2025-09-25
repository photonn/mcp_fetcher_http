#!/usr/bin/env python3
"""
Demo script to show the MCP server functionality without full MCP protocol
This demonstrates the core functionality of URL fetching and HTML to Markdown conversion.
"""

import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core import URLFetcher, HTMLToMarkdownConverter, is_valid_url


def create_sample_html():
    """Create a sample HTML string for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Page</title>
    </head>
    <body>
        <h1>Welcome to the Test Page</h1>
        <h2>Features</h2>
        <p>This is a <strong>sample HTML page</strong> to demonstrate the 
        <em>HTML to Markdown conversion</em> functionality.</p>
        
        <h3>List of Features:</h3>
        <ul>
            <li>Header conversion</li>
            <li><strong>Bold text</strong> support</li>
            <li><em>Italic text</em> support</li>
            <li>Link preservation: <a href="https://example.com">Example Link</a></li>
        </ul>
        
        <blockquote>
            This is a sample blockquote to show formatting preservation.
        </blockquote>
        
        <p>Visit our <a href="https://github.com">GitHub page</a> for more information.</p>
    </body>
    </html>
    """


def test_html_to_markdown_conversion():
    """Test the HTML to Markdown conversion directly."""
    print("Testing HTML to Markdown conversion...")
    print("=" * 50)
    
    # Create converter instance
    converter = HTMLToMarkdownConverter()
    
    # Convert sample HTML
    html_content = create_sample_html()
    markdown_result = converter.convert(html_content)
    
    print("Original HTML:")
    print(html_content[:200] + "...")
    print("\n" + "=" * 50)
    print("Converted Markdown:")
    print(markdown_result)
    print("=" * 50)
    
    return markdown_result


async def demo_server_functionality():
    """Demonstrate the server functionality."""
    print("\nDemonstrating MCP Server Functionality")
    print("=" * 50)
    
    # Test URL validation
    test_urls = [
        "https://www.example.com",
        "http://example.com/path",
        "ftp://invalid.com",
        "not-a-url",
        ""
    ]
    
    print("URL Validation Tests:")
    for url in test_urls:
        is_valid = is_valid_url(url)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {url:<30} -> {status}")
    
    print("\nError Handling Test:")
    try:
        # Test with invalid URL
        fetcher = URLFetcher()
        await fetcher.fetch_content("invalid-url")
    except ValueError as e:
        print(f"  ✓ Correctly handled invalid URL: {e}")
    
    print("\nServer is ready to handle MCP tool calls!")
    print("Use the 'fetch_url' tool with a valid URL to fetch and convert web pages.")


async def main():
    """Main demo function."""
    print("MCP HTTP Fetcher Server - Functionality Demo")
    print("=" * 60)
    
    # Test HTML to Markdown conversion
    test_html_to_markdown_conversion()
    
    # Demonstrate server functionality
    await demo_server_functionality()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully! 🎉")
    print("\nTo run the actual MCP server, use:")
    print("  python app/server.py")
    print("\nTo build and run with Docker:")
    print("  docker build -t mcp-fetcher-http .")
    print("  docker run -it mcp-fetcher-http")


if __name__ == "__main__":
    asyncio.run(main())