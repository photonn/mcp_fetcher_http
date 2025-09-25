"""
Core functionality for the MCP HTTP Fetcher.

This package contains the main business logic for fetching web pages
and converting them to Markdown format.
"""

from .fetcher import URLFetcher, is_valid_url
from .converter import HTMLToMarkdownConverter

__all__ = ["URLFetcher", "HTMLToMarkdownConverter", "is_valid_url"]