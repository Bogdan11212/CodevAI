import logging
from flask import request, jsonify
from api import api_bp
from utils.model_utils import get_language_model, predefined_errors
from config import Config

logger = logging.getLogger(__name__)

@api_bp.route('/check_errors', methods=['POST'])
def check_errors():
    """
    Check code for errors and provide suggestions
    
    Expected JSON payload:
    {
        "code": "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
        "language": "python"
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
        logger.debug(f"Processing error check request for language {language}")
        
        # Demo mode - check if we have predefined errors for this code
        errors = ["No specific errors detected"]
        suggestions = []
        corrected_code = code
        
        # Check if we have a predefined error fix for this code and language
        if language in predefined_errors and code in predefined_errors[language]:
            error_info = predefined_errors[language][code]
            errors = error_info["errors"]
            suggestions = error_info["suggestions"]
            corrected_code = error_info["corrected_code"]
        else:
            # Simple pattern-based error detection for demo
            if language == "python":
                if ":" not in code and "def " in code:
                    errors = ["SyntaxError: Missing colon in function definition"]
                    suggestions = ["Add a colon at the end of the function definition"]
                    corrected_code = code.replace("def ", "def ") + ":"
                elif "if " in code and ":" not in code:
                    errors = ["SyntaxError: Missing colon after conditional statement"]
                    suggestions = ["Add a colon after the conditional statement"]
            
            elif language == "javascript":
                if "{" not in code and "function" in code:
                    errors = ["SyntaxError: Missing opening brace"]
                    suggestions = ["Add an opening brace after the function declaration"]
                    corrected_code = code + " {"
        
        # Prepare response
        response = {
            "errors": errors,
            "suggestions": suggestions,
            "corrected_code": corrected_code,
            "language": language,
            "input_code": code,
            "demo_mode": True
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in error checking: {str(e)}")
        return jsonify({"error": f"Error checking failed: {str(e)}"}), 500
