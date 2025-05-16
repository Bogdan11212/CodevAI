"""
Continuous Learning System for CodevAI

This module allows the AI to gradually learn from the internet by:
1. Searching for programming-related content
2. Processing and storing knowledge in a structured format
3. Periodically updating the knowledge base based on feedback
4. Integrating new knowledge into responses
"""

import os
import json
import time
import datetime
import logging
import random
import threading
import traceback
from collections import deque
from urllib.parse import urlparse
import requests

from brain.web_access import get_webpage_content, search_programming_solutions, is_valid_url
from brain.cloudflare_ai import get_ai_thinking
from utils.learning_utils import record_model_update

# Set up logging
logger = logging.getLogger(__name__)

# Configuration for continuous learning
LEARNING_INTERVAL = int(os.environ.get("LEARNING_INTERVAL", 3600))  # Default: 1 hour
MAX_URLS_PER_SESSION = int(os.environ.get("MAX_URLS_PER_SESSION", 5))
KNOWLEDGE_FILE = "instance/knowledge_base.json"
LEARNING_ACTIVE = True

# Queue for storing discovered URLs
url_queue = deque(maxlen=1000)
# Set for tracking processed URLs to avoid duplicates
processed_urls = set()
# Knowledge base
knowledge_base = {
    "programming_languages": {},
    "libraries": {},
    "algorithms": {},
    "best_practices": {},
    "common_errors": {},
    "last_updated": None
}

# Thread for continuous learning
learning_thread = None
is_learning = False

def load_knowledge_base():
    """Load the knowledge base from file"""
    global knowledge_base
    try:
        if os.path.exists(KNOWLEDGE_FILE):
            with open(KNOWLEDGE_FILE, 'r') as f:
                knowledge_base = json.load(f)
                logger.info(f"Knowledge base loaded with {count_knowledge_items()} items")
        else:
            logger.info("No knowledge base found, creating a new one")
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(KNOWLEDGE_FILE), exist_ok=True)
            save_knowledge_base()
    except Exception as e:
        logger.error(f"Error loading knowledge base: {str(e)}")
        logger.debug(traceback.format_exc())

def save_knowledge_base():
    """Save the knowledge base to file"""
    try:
        with open(KNOWLEDGE_FILE, 'w') as f:
            json.dump(knowledge_base, f, indent=2)
        logger.info(f"Knowledge base saved with {count_knowledge_items()} items")
    except Exception as e:
        logger.error(f"Error saving knowledge base: {str(e)}")
        logger.debug(traceback.format_exc())

def count_knowledge_items():
    """Count total items in the knowledge base"""
    count = 0
    for category in knowledge_base:
        if category != "last_updated":
            count += len(knowledge_base[category])
    return count

def add_url_to_queue(url):
    """Add a URL to the learning queue"""
    if is_valid_url(url) and url not in processed_urls:
        url_queue.append(url)
        logger.debug(f"Added URL to queue: {url}")
        return True
    return False

def extract_knowledge_from_content(content, url, topic=None):
    """
    Extract structured knowledge from webpage content using Cloudflare AI

    Args:
        content (str): Webpage content
        url (str): Source URL
        topic (str, optional): Topic category

    Returns:
        dict: Extracted knowledge items
    """
    try:
        # Clean and normalize content
        if len(content) > 10000:
            content = content[:10000] + "..."

        # Extract code blocks
        import re
        code_blocks = re.findall(r'```[a-z]*\n(.*?)\n```', content, re.DOTALL)