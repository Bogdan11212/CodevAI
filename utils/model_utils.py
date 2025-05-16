import logging
from config import Config

logger = logging.getLogger(__name__)

# Dict with predefined completions for demo purposes
predefined_completions = {
    "python": {
        "def fibonacci(n):": """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)""",
        
        "def quicksort(arr):": """def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)""",
        
        "class Node:": """class Node:
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None"""
    },
    
    "javascript": {
        "function fibonacci(n) {": """function fibonacci(n) {
  if (n <= 0) return 0;
  if (n === 1) return 1;
  return fibonacci(n-1) + fibonacci(n-2);
}"""
    }
}

# Dict with predefined error fixes for demo
predefined_errors = {
    "python": {
        "def fibonacci(n)\n    if n <= 0:\n        return 0\n    elif n == 1\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)": {
            "errors": ["SyntaxError: Missing colon after function definition on line 1", 
                      "SyntaxError: Missing colon after 'elif n == 1' on line 4"],
            "suggestions": ["Add a colon after 'def fibonacci(n)'", 
                           "Add a colon after 'elif n == 1'"],
            "corrected_code": """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)"""
        }
    }
}

def get_language_model(language=None, task="completion"):
    """
    Simplified model function for demo purposes
    
    Args:
        language (str): Programming language (python, javascript, java, cpp, go)
        task (str): Task type (completion, error-detection, language-detection)
        
    Returns:
        tuple: (model, tokenizer) - In demo mode, returns None, None
    """
    logger.info(f"Demo mode: simulating model for {language} and {task}")
    return None, None

def get_language_model_version():
    """Get the current language model version information"""
    return {
        "version": "0.1.0-demo",
        "base_model": "Demo model - no real AI used",
        "supported_languages": Config.SUPPORTED_LANGUAGES,
        "last_updated": "2025-05-16"
    }

def update_model_weights(feedback_data):
    """
    Update model weights based on feedback (simulated)
    """
    logger.info(f"Demo mode: simulating model update with {len(feedback_data)} feedback items")
    
    return {
        "status": "success",
        "message": f"Demo mode: Model update simulated with {len(feedback_data)} feedback items",
        "new_version": "0.1.1-demo"
    }
