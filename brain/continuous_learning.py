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
        # Truncate content if it's too long
        if len(content) > 10000:
            content = content[:10000] + "..."
        
        # Determine relevant topics from URL
        domain = urlparse(url).netloc
        programming_languages = ["python", "javascript", "java", "cpp", "go", "rust", "php", "ruby"]
        detected_language = None
        
        for lang in programming_languages:
            if lang in url.lower() or lang in content.lower()[:1000]:
                detected_language = lang
                break
        
        # If no specific topic is provided, try to infer it
        if not topic:
            if "algorithm" in url.lower() or "algorithm" in content.lower()[:1000]:
                topic = "algorithms"
            elif "error" in url.lower() or "exception" in url.lower():
                topic = "common_errors"
            elif "best" in url.lower() and "practice" in url.lower():
                topic = "best_practices"
            elif detected_language:
                topic = "programming_languages"
            else:
                topic = "libraries"
        
        # Prepare prompt for Cloudflare AI
        prompt = f"""
        Extract programming knowledge from the following content from {domain}.
        
        CONTENT: 
        {content}
        
        Extract key information as JSON with the following structure:
        {{
            "topic": "{topic}",
            "key": "A unique identifier for this knowledge (e.g., 'python_list_comprehension', 'react_useeffect_hook')",
            "title": "A concise title for this knowledge",
            "language": "{detected_language if detected_language else 'general'}",
            "summary": "A comprehensive summary of the knowledge",
            "code_examples": ["Example 1", "Example 2"],
            "tags": ["tag1", "tag2"],
            "source": "{url}",
            "confidence": 0.9  // 0.0-1.0 rating of how confident you are in this extraction
        }}
        
        If multiple distinct knowledge items are found, return an array of such objects.
        Focus only on factual, programming-related knowledge. Confidence should be below 0.6 if the content is not directly related to programming.
        """
        
        # Get AI thinking
        result = get_ai_thinking(prompt, "general", 0)
        
        # Extract the answer
        if "answer" in result:
            try:
                # Try to parse JSON from the answer
                if isinstance(result["answer"], str):
                    # Clean the string to make it valid JSON
                    json_str = result["answer"]
                    
                    # Remove markdown code block markers if present
                    if "```json" in json_str:
                        json_str = json_str.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_str:
                        json_str = json_str.split("```")[1].split("```")[0].strip()
                    
                    extracted_data = json.loads(json_str)
                    
                    # Normalize the data structure
                    if isinstance(extracted_data, dict):
                        # Single knowledge item
                        return [extracted_data]
                    elif isinstance(extracted_data, list):
                        # Multiple knowledge items
                        return extracted_data
                else:
                    # Already a parsed JSON object
                    if isinstance(result["answer"], dict):
                        return [result["answer"]]
                    return result["answer"]
            except Exception as e:
                logger.error(f"Error parsing knowledge extraction result: {str(e)}")
                logger.debug(traceback.format_exc())
        
        return []
    except Exception as e:
        logger.error(f"Error extracting knowledge: {str(e)}")
        logger.debug(traceback.format_exc())
        return []

def add_knowledge_to_base(knowledge_items):
    """
    Add extracted knowledge to the knowledge base
    
    Args:
        knowledge_items (list): List of knowledge item dictionaries
        
    Returns:
        int: Number of items added
    """
    added_count = 0
    
    for item in knowledge_items:
        try:
            # Validate the item has required fields
            if not all(field in item for field in ["topic", "key", "title", "summary"]):
                continue
                
            # Skip low-confidence items
            if "confidence" in item and item["confidence"] < 0.6:
                continue
                
            topic = item["topic"]
            key = item["key"]
            
            # Map topic to our knowledge base categories
            if topic in ["programming_language", "language"]:
                category = "programming_languages"
            elif topic in ["library", "framework", "package"]:
                category = "libraries"
            elif topic in ["algorithm", "data_structure"]:
                category = "algorithms"
            elif topic in ["best_practice", "pattern", "convention"]:
                category = "best_practices"
            elif topic in ["error", "exception", "bug", "common_error"]:
                category = "common_errors"
            else:
                # Try to match with existing categories
                if topic in knowledge_base:
                    category = topic
                else:
                    # Determine best category
                    if "error" in key.lower() or "exception" in key.lower():
                        category = "common_errors"
                    elif "algorithm" in key.lower():
                        category = "algorithms"
                    elif "practice" in key.lower():
                        category = "best_practices"
                    else:
                        # Default to libraries if can't determine
                        category = "libraries"
            
            # Clean up the knowledge item
            cleaned_item = {
                "title": item["title"],
                "summary": item["summary"],
                "language": item.get("language", "general"),
                "code_examples": item.get("code_examples", []),
                "tags": item.get("tags", []),
                "source": item.get("source", ""),
                "confidence": item.get("confidence", 0.7),
                "added": datetime.datetime.now().isoformat(),
                "usage_count": 0
            }
            
            # Add to knowledge base
            if category not in knowledge_base:
                knowledge_base[category] = {}
                
            knowledge_base[category][key] = cleaned_item
            added_count += 1
            
        except Exception as e:
            logger.error(f"Error adding knowledge item: {str(e)}")
            logger.debug(traceback.format_exc())
    
    # Update last updated timestamp
    knowledge_base["last_updated"] = datetime.datetime.now().isoformat()
    
    # Save to file if items were added
    if added_count > 0:
        save_knowledge_base()
        
    return added_count

def process_url():
    """Process a URL from the queue and extract knowledge"""
    global processed_urls
    
    if not url_queue:
        return 0
    
    url = url_queue.popleft()
    
    # Skip if already processed
    if url in processed_urls:
        return 0
    
    try:
        # Get webpage content
        content = get_webpage_content(url)
        if not content:
            logger.warning(f"Failed to retrieve content from {url}")
            return 0
            
        # Extract knowledge
        knowledge_items = extract_knowledge_from_content(content, url)
        
        # Add to knowledge base
        added_count = add_knowledge_to_base(knowledge_items)
        
        # Mark as processed
        processed_urls.add(url)
        
        # Extract links for further exploration
        extract_and_queue_links(content, url)
        
        return added_count
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        logger.debug(traceback.format_exc())
        return 0

def extract_and_queue_links(content, source_url):
    """Extract links from content and add relevant ones to the queue"""
    try:
        # Extract links using simple regex for demonstration
        import re
        links = re.findall(r'href=[\'"]?([^\'" >]+)', content)
        
        # Process each link
        for link in links:
            # Convert relative URLs to absolute
            if link.startswith('/'):
                # Get the base URL
                parsed_url = urlparse(source_url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                link = f"{base_url}{link}"
            
            # Add relevant programming-related URLs to queue
            if is_valid_url(link) and is_programming_related(link):
                add_url_to_queue(link)
    except Exception as e:
        logger.error(f"Error extracting links: {str(e)}")

def is_programming_related(url):
    """Check if a URL is likely to contain programming content"""
    programming_terms = [
        "python", "javascript", "java", "cpp", "algorithm", "programming",
        "code", "developer", "software", "library", "framework", "api",
        "function", "class", "object", "variable", "database", "sql",
        "tutorial", "guide", "documentation", "stack", "overflow", "github"
    ]
    
    url_lower = url.lower()
    
    # Check domain
    parsed_url = urlparse(url_lower)
    domain = parsed_url.netloc
    
    # Whitelist certain domains
    whitelisted_domains = [
        "github.com", "stackoverflow.com", "medium.com", "dev.to",
        "realpython.com", "mozilla.org", "w3schools.com", "geeksforgeeks.org",
        "hackernoon.com", "freecodecamp.org", "css-tricks.com",
        "developer.mozilla.org", "docs.python.org"
    ]
    
    for white_domain in whitelisted_domains:
        if white_domain in domain:
            return True
    
    # Check for programming terms in URL
    for term in programming_terms:
        if term in url_lower:
            return True
    
    return False

def search_and_learn(query=None):
    """
    Actively search for programming content and learn from it
    
    Args:
        query (str, optional): Search query
        
    Returns:
        int: Number of items added to knowledge base
    """
    try:
        if not query:
            # Generate a random query if none provided
            topics = [
                "python best practices", "javascript async patterns",
                "error handling in go", "modern c++ features",
                "rust memory management", "java stream api",
                "react hooks tutorial", "sql query optimization",
                "data structures explained", "clean code principles",
                "typescript advanced types", "web security best practices"
            ]
            query = random.choice(topics)
        
        # Search for programming solutions
        search_results = search_programming_solutions(query)
        
        if not search_results:
            logger.warning(f"No search results for query: {query}")
            return 0
        
        # Add search result URLs to queue
        for result in search_results:
            if "url" in result:
                add_url_to_queue(result["url"])
        
        # Process some URLs from the queue
        added_count = 0
        for _ in range(min(MAX_URLS_PER_SESSION, len(url_queue))):
            added_count += process_url()
        
        return added_count
    except Exception as e:
        logger.error(f"Error in search_and_learn: {str(e)}")
        logger.debug(traceback.format_exc())
        return 0

def continuous_learning_task():
    """Background task for continuous learning"""
    global is_learning
    
    logger.info("Starting continuous learning task")
    is_learning = True
    
    try:
        # Load existing knowledge
        load_knowledge_base()
        
        # Track learning metrics
        total_added = 0
        session_start = time.time()
        
        # Perform initial search and learning
        topics = [
            "python programming", "javascript development",
            "web development", "algorithm design", 
            "software architecture", "database optimization"
        ]
        
        for topic in topics:
            added = search_and_learn(topic)
            total_added += added
            logger.info(f"Learned {added} items from topic: {topic}")
            
            # Short pause between searches
            time.sleep(5)
            
            # Break if we've added a good amount of knowledge
            if total_added > 50:
                break
        
        # Record model update
        duration = time.time() - session_start
        record_model_update("continuous_learning", 
                           {"items_added": total_added, "duration": duration}, 
                           total_added)
                           
        logger.info(f"Initial learning complete. Added {total_added} items in {duration:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error in continuous learning task: {str(e)}")
        logger.debug(traceback.format_exc())
    finally:
        is_learning = False

def get_knowledge(topic=None, language=None, query=None, limit=5):
    """
    Retrieve knowledge from the knowledge base
    
    Args:
        topic (str, optional): Knowledge category
        language (str, optional): Programming language
        query (str, optional): Search query
        limit (int): Maximum number of items to return
        
    Returns:
        list: Knowledge items matching the criteria
    """
    try:
        # Load knowledge base if not loaded
        if "last_updated" not in knowledge_base:
            load_knowledge_base()
            
        results = []
        
        # If a specific topic is requested
        if topic and topic in knowledge_base:
            category = knowledge_base[topic]
            
            for key, item in category.items():
                # Filter by language if specified
                if language and item.get("language") != language:
                    continue
                
                # Filter by query if specified
                if query and not search_in_item(item, query):
                    continue
                
                # Add to results
                results.append({
                    "topic": topic,
                    "key": key,
                    **item
                })
                
                # Increment usage count
                item["usage_count"] = item.get("usage_count", 0) + 1
                
                # Break if we've reached the limit
                if len(results) >= limit:
                    break
        else:
            # Search across all categories
            for category_name, category in knowledge_base.items():
                if category_name == "last_updated":
                    continue
                    
                for key, item in category.items():
                    # Filter by language if specified
                    if language and item.get("language") != language:
                        continue
                    
                    # Filter by query if specified
                    if query and not search_in_item(item, query):
                        continue
                    
                    # Add to results
                    results.append({
                        "topic": category_name,
                        "key": key,
                        **item
                    })
                    
                    # Increment usage count
                    item["usage_count"] = item.get("usage_count", 0) + 1
                    
                    # Break if we've reached the limit
                    if len(results) >= limit:
                        break
                
                # Break if we've reached the limit
                if len(results) >= limit:
                    break
        
        # Sort by usage count and confidence
        results.sort(key=lambda x: (x.get("usage_count", 0), x.get("confidence", 0)), reverse=True)
        
        # Limit results
        results = results[:limit]
        
        # Update knowledge base file with updated usage counts
        save_knowledge_base()
        
        return results
    except Exception as e:
        logger.error(f"Error retrieving knowledge: {str(e)}")
        logger.debug(traceback.format_exc())
        return []

def search_in_item(item, query):
    """Search for a query in a knowledge item"""
    query = query.lower()
    
    # Search in title
    if query in item.get("title", "").lower():
        return True
        
    # Search in summary
    if query in item.get("summary", "").lower():
        return True
        
    # Search in tags
    for tag in item.get("tags", []):
        if query in tag.lower():
            return True
            
    # Search in code examples
    for example in item.get("code_examples", []):
        if query in example.lower():
            return True
            
    return False

def start_continuous_learning():
    """Start the continuous learning thread"""
    global learning_thread
    
    if learning_thread is None or not learning_thread.is_alive():
        learning_thread = threading.Thread(target=continuous_learning_task)
        learning_thread.daemon = True
        learning_thread.start()
        logger.info("Continuous learning thread started")
        return True
    else:
        logger.info("Continuous learning thread already running")
        return False

def get_learning_status():
    """Get the status of the continuous learning system"""
    # Load knowledge base if not loaded
    if "last_updated" not in knowledge_base:
        load_knowledge_base()
    
    return {
        "is_learning": is_learning,
        "knowledge_items": count_knowledge_items(),
        "categories": {
            category: len(items) for category, items in knowledge_base.items() 
            if category != "last_updated"
        },
        "last_updated": knowledge_base.get("last_updated"),
        "queue_size": len(url_queue),
        "processed_urls": len(processed_urls)
    }

def enhance_ai_response(response, language=None):
    """
    Enhance AI responses with knowledge from the knowledge base
    
    Args:
        response (dict): Original AI response
        language (str, optional): Programming language
        
    Returns:
        dict: Enhanced response with additional knowledge
    """
    try:
        # Don't modify if no answer
        if "answer" not in response:
            return response
            
        # Get the original answer
        answer = response["answer"]
        
        # Extract key terms from the answer
        query = extract_key_terms(answer)
        
        # Get relevant knowledge
        knowledge = get_knowledge(language=language, query=query, limit=2)
        
        if not knowledge:
            return response
            
        # Enhance the response
        enhanced_response = response.copy()
        
        # Add knowledge to response
        if "knowledge" not in enhanced_response:
            enhanced_response["knowledge"] = []
            
        enhanced_response["knowledge"].extend(knowledge)
        
        # Add a note about the knowledge
        if len(knowledge) > 0:
            knowledge_note = "\n\nAdditional relevant information:\n"
            
            for item in knowledge:
                knowledge_note += f"\n- {item['title']}: {item['summary'][:100]}..."
                if item.get("code_examples") and len(item["code_examples"]) > 0:
                    knowledge_note += f"\n  Example: {item['code_examples'][0][:100]}..."
                    
            enhanced_response["answer"] = answer + knowledge_note
        
        return enhanced_response
    except Exception as e:
        logger.error(f"Error enhancing AI response: {str(e)}")
        logger.debug(traceback.format_exc())
        return response

def extract_key_terms(text):
    """Extract key programming terms from text"""
    # Simple version - just use the first 100 characters
    return text[:100]

# Initialize the system
load_knowledge_base()