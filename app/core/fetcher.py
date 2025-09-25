"""
URL fetching functionality for the MCP HTTP Fetcher.

This module provides utilities for validating URLs and fetching web content.
"""

import logging
from typing import Optional
from urllib.parse import urlparse
import aiohttp

logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    """Validate if the provided string is a valid HTTP/HTTPS URL.
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


class URLFetcher:
    """Handles fetching content from URLs with proper error handling."""
    
    def __init__(self, timeout: int = 30):
        """Initialize the URL fetcher.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    async def fetch_content(self, url: str) -> str:
        """Fetch HTML content from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string
            
        Raises:
            ValueError: If the URL is invalid
            Exception: If fetching fails due to network or HTTP errors
        """
        if not is_valid_url(url):
            raise ValueError(f"Invalid URL provided: {url}")
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: Failed to fetch {url}")
                    
                    # Get the content type to ensure it's HTML-like
                    content_type = response.headers.get('content-type', '').lower()
                    if 'html' not in content_type and 'xml' not in content_type:
                        logger.warning(f"Content type '{content_type}' may not be HTML")
                    
                    # Read the response content
                    html_content = await response.text()
                    
                    logger.info(f"Successfully fetched {url} ({len(html_content)} characters)")
                    return html_content
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Network error while fetching {url}: {str(e)}")
        except Exception as e:
            if "Invalid URL" in str(e):
                raise
            raise Exception(f"Error processing {url}: {str(e)}")