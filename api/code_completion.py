import logging
from flask import request, jsonify
from api import api_bp
from utils.model_utils import get_language_model, predefined_completions
from config import Config

logger = logging.getLogger(__name__)

@api_bp.route('/complete', methods=['POST'])
def complete_code():
    """
    Complete code based on the provided snippet
    
    Expected JSON payload:
    {
        "code": "def fibonacci(n):",
        "language": "python",
        "max_tokens": 100
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Extract parameters
    code = data.get('code')
    language = data.get('language', 'python').lower()
    
    # Validate input
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    if language not in Config.SUPPORTED_LANGUAGES:
        return jsonify({
            "error": f"Unsupported language. Supported languages are: {', '.join(Config.SUPPORTED_LANGUAGES)}"
        }), 400
    
    try:
        logger.debug(f"Processing code completion request for language {language}")
        
        # Demo mode - look for predefined completions
        completion = ""
        
        # Check if we have a predefined completion for this code and language
        if language in predefined_completions and code in predefined_completions[language]:
            completion = predefined_completions[language][code]
        else:
            # Provide a generic completion for demo
            if language == "python":
                completion = "    # This is a demo completion\n    pass"
            elif language == "javascript":
                completion = "  // This is a demo completion\n  return null;"
            elif language == "java":
                completion = "  // This is a demo completion\n  return null;"
            elif language == "cpp":
                completion = "  // This is a demo completion\n  return 0;"
            elif language == "go":
                completion = "  // This is a demo completion\n  return nil"
        
        # Prepare response
        response = {
            "completion": completion,
            "language": language,
            "input_code": code,
            "demo_mode": True
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in code completion: {str(e)}")
        return jsonify({"error": f"Code completion failed: {str(e)}"}), 500
