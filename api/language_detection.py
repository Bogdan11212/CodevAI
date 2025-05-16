import logging
from flask import request, jsonify
from api import api_bp
from utils.model_utils import get_language_model
from config import Config

logger = logging.getLogger(__name__)

@api_bp.route('/detect_language', methods=['POST'])
def detect_language():
    """
    Detect the programming language of the provided code
    
    Expected JSON payload:
    {
        "code": "function factorial(n) {\n  if (n === 0 || n === 1) {\n    return 1;\n  }\n  return n * factorial(n - 1);\n}"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Extract parameters
    code = data.get('code')
    
    # Validate input
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    try:
        # Demo mode - simple rule-based language detection
        logger.debug("Processing language detection request in demo mode")
        
        # Simple pattern-based language detection
        detected_language = "unknown"
        confidence = 0.7  # Default confidence
        
        # Very simple pattern checks for demo purposes
        if "def " in code or "import " in code or "class " in code and ":" in code:
            detected_language = "python"
            confidence = 0.95
        elif "function " in code or "var " in code or "let " in code or "const " in code:
            detected_language = "javascript" 
            confidence = 0.9
        elif "public class " in code or "private " in code or "protected " in code:
            detected_language = "java"
            confidence = 0.9
        elif "#include" in code or "int main" in code:
            detected_language = "cpp"
            confidence = 0.9
        elif "package " in code or "func " in code:
            detected_language = "go"
            confidence = 0.85
        
        # Check if detected language is in our supported list
        supported = detected_language in Config.SUPPORTED_LANGUAGES
        
        logger.debug(f"Detected language: {detected_language}, supported: {supported}")
        
        # Prepare response
        response = {
            "detected_language": detected_language,
            "supported": supported,
            "confidence": confidence,
            "demo_mode": True
        }
        
        if not supported:
            response["supported_languages"] = Config.SUPPORTED_LANGUAGES
            
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in language detection: {str(e)}")
        return jsonify({"error": f"Language detection failed: {str(e)}"}), 500
