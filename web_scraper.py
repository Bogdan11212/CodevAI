"""
Web Scraper for CodevAI

This module provides functionality for extracting and processing content
from web pages for the CodevAI AI learning system.
"""

import logging
import trafilatura
from brain.continuous_learning import add_url_to_queue, process_url
from brain.web_access import is_valid_url

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a URL and returns the main text content of the website.
    The text content is extracted using trafilatura and is easier to understand.
    The results are not meant for direct reading, better to summarize them through LLM
    before use.

    Some popular sites to get information from:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    if not is_valid_url(url):
        logger.error(f"Invalid URL: {url}")
        return "Error: Invalid URL"
    
    try:
        # Send request to the website
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.error(f"Failed to load page: {url}")
            return "Error: Failed to load page"
        
        # Extract text content
        text = trafilatura.extract(downloaded)
        
        # Add URL to learning queue
        add_url_to_queue(url)
        
        return text if text else "Failed to extract content"
    except Exception as e:
        logger.error(f"Error getting web page content {url}: {str(e)}")
        return f"Error processing URL: {str(e)}"

def enqueue_url_for_learning(url: str) -> bool:
    """
    Adds URL to the queue for processing by continuous learning system
    
    Args:
        url (str): URL to add
        
    Returns:
        bool: True if URL was added successfully, False otherwise
    """
    if not is_valid_url(url):
        logger.error(f"Invalid URL for learning: {url}")
        return False
    
    return add_url_to_queue(url)

def process_url_now(url: str) -> dict:
    """
    Immediately processes URL for knowledge extraction
    
    Args:
        url (str): URL to process
        
    Returns:
        dict: Processing result or None in case of error
    """
    if not is_valid_url(url):
        logger.error(f"Invalid URL for immediate processing: {url}")
        return {"success": False, "error": "Invalid URL"}
    
    success = process_url(url)
    if success:
        return {"success": True, "message": "URL successfully processed"}
    else:
        return {"success": False, "error": "Failed to process URL"}