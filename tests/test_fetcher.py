#!/usr/bin/env python3
"""
Test module for URL fetching functionality.

This script tests the URLFetcher class and URL validation functions.
"""

import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.fetcher import URLFetcher, is_valid_url


async def test_url_validation():
    """Test URL validation function."""
    print("Testing URL validation...")
    
    valid_urls = [
        "https://www.example.com",
        "http://example.com",
        "https://example.com/path?param=value",
        "https://subdomain.example.com:8080/path"
    ]
    
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",  # Valid URL but not HTTP/HTTPS
        "",
        "example.com",  # Missing protocol
        "http://",  # Missing netloc
        "https:///path"  # Missing netloc
    ]
    
    for url in valid_urls:
        assert is_valid_url(url), f"Expected {url} to be valid"
        print(f"✓ {url} is valid")
    
    for url in invalid_urls:
        assert not is_valid_url(url), f"Expected {url} to be invalid"
        print(f"✓ {url} is correctly identified as invalid")
    
    print("URL validation tests passed!\n")


async def test_fetcher_initialization():
    """Test URLFetcher initialization."""
    print("Testing URLFetcher initialization...")
    
    # Test default initialization
    fetcher1 = URLFetcher()
    assert fetcher1.timeout == 30, "Default timeout should be 30 seconds"
    print("✓ Default initialization works")
    
    # Test custom timeout
    fetcher2 = URLFetcher(timeout=60)
    assert fetcher2.timeout == 60, "Custom timeout should be set correctly"
    print("✓ Custom timeout initialization works")
    
    print("URLFetcher initialization tests passed!\n")


async def test_fetcher_error_handling():
    """Test URLFetcher error handling."""
    print("Testing URLFetcher error handling...")
    
    fetcher = URLFetcher()
    
    # Test invalid URL rejection
    try:
        await fetcher.fetch_content("invalid-url")
        assert False, "Should have raised ValueError for invalid URL"
    except ValueError as e:
        assert "Invalid URL provided" in str(e)
        print("✓ Correctly rejected invalid URL")
    
    # Test empty URL rejection
    try:
        await fetcher.fetch_content("")
        assert False, "Should have raised ValueError for empty URL"
    except ValueError as e:
        assert "Invalid URL provided" in str(e)
        print("✓ Correctly rejected empty URL")
    
    print("URLFetcher error handling tests passed!\n")


async def main():
    """Run all fetcher tests."""
    print("Running URLFetcher tests...\n")
    
    await test_url_validation()
    await test_fetcher_initialization()
    await test_fetcher_error_handling()
    
    print("All URLFetcher tests passed! 🎉")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)