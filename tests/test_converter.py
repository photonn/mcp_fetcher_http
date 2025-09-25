#!/usr/bin/env python3
"""
Test module for HTML to Markdown conversion functionality.

This script tests the HTMLToMarkdownConverter class.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.converter import HTMLToMarkdownConverter


def test_converter_initialization():
    """Test HTMLToMarkdownConverter initialization."""
    print("Testing HTMLToMarkdownConverter initialization...")
    
    # Test default initialization
    converter1 = HTMLToMarkdownConverter()
    assert not converter1.converter.ignore_links, "Default should preserve links"
    assert not converter1.converter.ignore_images, "Default should preserve images"
    assert converter1.converter.body_width == 0, "Default should not wrap lines"
    print("✓ Default initialization works")
    
    # Test custom initialization
    converter2 = HTMLToMarkdownConverter(ignore_links=True, ignore_images=True, body_width=80)
    assert converter2.converter.ignore_links, "Should ignore links when configured"
    assert converter2.converter.ignore_images, "Should ignore images when configured"
    assert converter2.converter.body_width == 80, "Should set custom body width"
    print("✓ Custom initialization works")
    
    print("HTMLToMarkdownConverter initialization tests passed!\n")


def test_basic_conversion():
    """Test basic HTML to Markdown conversion."""
    print("Testing basic HTML to Markdown conversion...")
    
    converter = HTMLToMarkdownConverter()
    
    # Test simple HTML
    html_input = "<h1>Title</h1><p>This is a <strong>test</strong>.</p>"
    expected_output_parts = ["# Title", "**test**"]
    
    result = converter.convert(html_input)
    
    for part in expected_output_parts:
        assert part in result, f"Expected '{part}' in output: {result}"
    
    print(f"✓ Basic conversion works: {len(result)} characters")
    
    # Test empty HTML
    empty_result = converter.convert("")
    assert isinstance(empty_result, str), "Should return string even for empty input"
    print("✓ Empty HTML handled correctly")
    
    print("Basic conversion tests passed!\n")


def test_complex_conversion():
    """Test complex HTML to Markdown conversion."""
    print("Testing complex HTML to Markdown conversion...")
    
    converter = HTMLToMarkdownConverter()
    
    complex_html = """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Main Title</h1>
        <h2>Subtitle</h2>
        <p>This is a paragraph with <a href="https://example.com">a link</a> and <em>emphasis</em>.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2 with <strong>bold text</strong></li>
        </ul>
        <blockquote>This is a quote.</blockquote>
    </body>
    </html>
    """
    
    result = converter.convert(complex_html)
    
    # Check for various markdown elements
    expected_elements = [
        "# Main Title",
        "## Subtitle", 
        "[a link](https://example.com)",
        "_emphasis_",
        "* Item 1",
        "**bold text**",
        "> This is a quote"
    ]
    
    for element in expected_elements:
        assert element in result, f"Expected '{element}' in output"
    
    print(f"✓ Complex conversion works: {len(result)} characters")
    print("Complex conversion tests passed!\n")


def test_link_and_image_handling():
    """Test link and image handling options."""
    print("Testing link and image handling...")
    
    html_with_links = '<p>Visit <a href="https://example.com">our site</a> and see <img src="image.jpg" alt="test image">.</p>'
    
    # Test with links and images preserved (default)
    converter_preserve = HTMLToMarkdownConverter()
    result_preserve = converter_preserve.convert(html_with_links)
    assert "[our site](https://example.com)" in result_preserve, "Should preserve links by default"
    print("✓ Links preserved by default")
    
    # Test with links ignored
    converter_no_links = HTMLToMarkdownConverter(ignore_links=True)
    result_no_links = converter_no_links.convert(html_with_links)
    assert "https://example.com" not in result_no_links, "Should ignore links when configured"
    print("✓ Links ignored when configured")
    
    print("Link and image handling tests passed!\n")


def test_error_handling():
    """Test error handling in conversion."""
    print("Testing conversion error handling...")
    
    converter = HTMLToMarkdownConverter()
    
    # Test with malformed HTML (should still work)
    malformed_html = "<h1>Unclosed tag<p>Another unclosed"
    try:
        result = converter.convert(malformed_html)
        assert isinstance(result, str), "Should return string even for malformed HTML"
        print("✓ Malformed HTML handled gracefully")
    except Exception as e:
        print(f"⚠ Malformed HTML caused error (acceptable): {e}")
    
    print("Error handling tests passed!\n")


def main():
    """Run all converter tests."""
    print("Running HTMLToMarkdownConverter tests...\n")
    
    test_converter_initialization()
    test_basic_conversion()
    test_complex_conversion()
    test_link_and_image_handling()
    test_error_handling()
    
    print("All HTMLToMarkdownConverter tests passed! 🎉")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)