import logging
import time
from flask import request, jsonify
from api import api_bp
from config import Config
from brain.cloudflare_ai import get_code_completion

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
    max_tokens = data.get('max_tokens', 100)
    
    # Validate input
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    if language not in Config.SUPPORTED_LANGUAGES:
        return jsonify({
            "error": f"Unsupported language. Supported languages are: {', '.join(Config.SUPPORTED_LANGUAGES)}"
        }), 400
    
    try:
        logger.debug(f"Processing code completion request for language {language}")
        
        start_time = time.time()
        
        # Используем Cloudflare AI для завершения кода
        completion = get_code_completion(code, language, max_tokens)
        
        # Расчитываем время обработки
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            "completion": completion,
            "language": language,
            "input_code": code,
            "processing_time": processing_time,
            "demo_mode": False
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in code completion: {str(e)}")
        return jsonify({"error": f"Code completion failed: {str(e)}"}), 500
