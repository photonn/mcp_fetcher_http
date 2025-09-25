"""
HTML to Markdown conversion functionality.

This module provides utilities for converting HTML content to Markdown format.
"""

import logging
import html2text

logger = logging.getLogger(__name__)


class HTMLToMarkdownConverter:
    """Converts HTML content to Markdown format."""
    
    def __init__(self, ignore_links: bool = False, ignore_images: bool = False, body_width: int = 0):
        """Initialize the HTML to Markdown converter.
        
        Args:
            ignore_links: Whether to ignore links in the conversion
            ignore_images: Whether to ignore images in the conversion  
            body_width: Maximum line width (0 = no wrapping)
        """
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = ignore_links
        self.converter.ignore_images = ignore_images
        self.converter.body_width = body_width
    
    def convert(self, html_content: str) -> str:
        """Convert HTML content to Markdown.
        
        Args:
            html_content: HTML content as string
            
        Returns:
            Markdown content as string
        """
        try:
            markdown_content = self.converter.handle(html_content)
            logger.info(f"Successfully converted HTML to Markdown ({len(markdown_content)} characters)")
            return markdown_content
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}")
            raise Exception(f"Failed to convert HTML to Markdown: {str(e)}")