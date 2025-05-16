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
import re

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
        code_blocks = re.findall(r'```[a-z]*\n(.*?)\n```', content, re.DOTALL)
        
        # Prepare prompt for AI to extract knowledge
        domain = urlparse(url).netloc
        prompt = f"""
        Extract structured knowledge from this programming article. The source is {domain}.
        
        Content:
        {content[:3000]}
        
        Extract the following types of knowledge:
        1. Programming concepts and patterns
        2. Best practices
        3. Common errors and solutions
        4. Library and framework features
        5. Algorithms and data structures
        
        Format the output as JSON with appropriate categories and brief explanations.
        """
        
        # Use AI to extract knowledge
        try:
            ai_response = get_ai_thinking(prompt, "general", 1)
            if "response" in ai_response:
                try:
                    extracted_knowledge = json.loads(ai_response["response"])
                    extracted_knowledge["source_url"] = url
                    extracted_knowledge["timestamp"] = datetime.datetime.now().isoformat()
                    return extracted_knowledge
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse AI response as JSON from {url}")
        except Exception as e:
            logger.warning(f"Error using AI to extract knowledge: {str(e)}")
        
        # Fallback to simple extraction
        return {
            "source_url": url,
            "timestamp": datetime.datetime.now().isoformat(),
            "content_snippet": content[:200],
            "code_samples": code_blocks[:3] if code_blocks else []
        }
    except Exception as e:
        logger.error(f"Error extracting knowledge from {url}: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def update_knowledge_base(knowledge_data, category=None):
    """
    Update the knowledge base with new information
    
    Args:
        knowledge_data (dict): Knowledge data to add
        category (str, optional): Category to add the knowledge to
    """
    if not knowledge_data:
        return
    
    try:
        # If category provided, add to that category
        if category and category in knowledge_base:
            key = f"{category}_{len(knowledge_base[category]) + 1}"
            knowledge_base[category][key] = knowledge_data
        # Otherwise, try to organize automatically
        else:
            # Check for code samples
            if "code_samples" in knowledge_data and knowledge_data["code_samples"]:
                key = f"algorithms_{len(knowledge_base['algorithms']) + 1}"
                knowledge_base["algorithms"][key] = knowledge_data
            # Check for best practices
            elif "best_practices" in knowledge_data or "best practice" in str(knowledge_data).lower():
                key = f"best_practices_{len(knowledge_base['best_practices']) + 1}"
                knowledge_base["best_practices"][key] = knowledge_data
            # Check for errors
            elif "error" in str(knowledge_data).lower() or "exception" in str(knowledge_data).lower():
                key = f"common_errors_{len(knowledge_base['common_errors']) + 1}"
                knowledge_base["common_errors"][key] = knowledge_data
            # Check for libraries
            elif "library" in str(knowledge_data).lower() or "framework" in str(knowledge_data).lower():
                key = f"libraries_{len(knowledge_base['libraries']) + 1}"
                knowledge_base["libraries"][key] = knowledge_data
            # Default to programming languages
            else:
                key = f"programming_languages_{len(knowledge_base['programming_languages']) + 1}"
                knowledge_base["programming_languages"][key] = knowledge_data
        
        # Update timestamp
        knowledge_base["last_updated"] = datetime.datetime.now().isoformat()
        logger.debug(f"Knowledge base updated with new data in category: {category}")
        return True
    except Exception as e:
        logger.error(f"Error updating knowledge base: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def process_url(url):
    """
    Process a URL to extract knowledge
    
    Args:
        url (str): URL to process
    
    Returns:
        bool: True if processing successful, False otherwise
    """
    if url in processed_urls:
        logger.debug(f"URL already processed: {url}")
        return False
    
    try:
        logger.info(f"Processing URL: {url}")
        
        # Get content from the URL
        content = get_webpage_content(url)
        if not content:
            logger.warning(f"No content retrieved from URL: {url}")
            processed_urls.add(url)
            return False
        
        # Extract knowledge from content
        knowledge = extract_knowledge_from_content(content, url)
        if not knowledge:
            logger.warning(f"Failed to extract knowledge from URL: {url}")
            processed_urls.add(url)
            return False
        
        # Determine category based on URL
        category = None
        domain = urlparse(url).netloc
        path = urlparse(url).path.lower()
        
        if "python" in domain or "python" in path:
            category = "programming_languages"
        elif "javascript" in domain or "js" in path:
            category = "programming_languages"
        elif "algorithm" in path:
            category = "algorithms"
        elif "error" in path or "exception" in path:
            category = "common_errors"
        elif "practice" in path or "guide" in path:
            category = "best_practices"
        elif "library" in path or "framework" in path:
            category = "libraries"
        
        # Update knowledge base
        update_knowledge_base(knowledge, category)
        
        # Mark URL as processed
        processed_urls.add(url)
        
        # Save knowledge base
        save_knowledge_base()
        
        return True
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        logger.debug(traceback.format_exc())
        processed_urls.add(url)
        return False

def discover_new_urls():
    """Discover new URLs to process based on popular programming topics"""
    try:
        # Popular programming topics to search for
        topics = [
            "python best practices",
            "javascript modern patterns",
            "java programming tips",
            "go language tutorial",
            "rust programming guide",
            "common programming errors",
            "clean code principles",
            "data structures algorithms",
            "machine learning basics",
            "web development frameworks"
        ]
        
        # Randomly select topics to search for
        selected_topics = random.sample(topics, min(3, len(topics)))
        
        for topic in selected_topics:
            # Search for programming solutions
            results = search_programming_solutions(topic)
            if results:
                # Add URLs to queue
                for result in results:
                    if "url" in result:
                        add_url_to_queue(result["url"])
                        
        logger.info(f"Discovered {len(url_queue)} URLs for processing")
    except Exception as e:
        logger.error(f"Error discovering new URLs: {str(e)}")
        logger.debug(traceback.format_exc())

def continuous_learning_task():
    """Function that runs in a background thread for continuous learning"""
    global is_learning
    
    if is_learning:
        logger.debug("Continuous learning task already running")
        return
    
    is_learning = True
    try:
        logger.info("Starting continuous learning task")
        
        # Load the knowledge base
        load_knowledge_base()
        
        # Discover new URLs if queue is empty
        if len(url_queue) == 0:
            discover_new_urls()
        
        # Process URLs in the queue
        urls_processed = 0
        while urls_processed < MAX_URLS_PER_SESSION and url_queue:
            url = url_queue.popleft()
            if process_url(url):
                urls_processed += 1
                # Small delay to avoid overwhelming resources
                time.sleep(2)
        
        # Record model update - skipping database recording due to context issues
        if urls_processed > 0:
            # No need to use record_model_update since it requires app context
            # Just log the info instead
            logger.info(f"Continuous learning completed. Processed {urls_processed} URLs.")
        
        is_learning = False
    except Exception as e:
        logger.error(f"Error in continuous learning task: {str(e)}")
        logger.debug(traceback.format_exc())
        is_learning = False

def start_continuous_learning_thread():
    """Start the continuous learning process in a background thread"""
    global learning_thread
    
    if learning_thread and learning_thread.is_alive():
        logger.debug("Learning thread already running")
        return
    
    # Create and start the thread
    learning_thread = threading.Thread(target=continuous_learning_task)
    learning_thread.daemon = True  # Thread will exit when main program exits
    learning_thread.start()
    logger.info("Continuous learning thread started")

def start_continuous_learning():
    """
    Initialize the continuous learning system
    """
    try:
        # Load the knowledge base
        load_knowledge_base()
        
        # Start learning thread
        start_continuous_learning_thread()
        
        # Start a timer to run the learning task periodically
        def schedule_learning():
            while LEARNING_ACTIVE:
                # Run learning task
                start_continuous_learning_thread()
                # Wait for the next interval
                time.sleep(LEARNING_INTERVAL)
        
        # Create and start the scheduler thread
        scheduler_thread = threading.Thread(target=schedule_learning)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("Continuous learning system initialized")
    except Exception as e:
        logger.error(f"Error initializing continuous learning: {str(e)}")
        logger.debug(traceback.format_exc())