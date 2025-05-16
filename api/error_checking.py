import logging
import time
from flask import request, jsonify
from api import api_bp
from config import Config
from brain.cloudflare_ai import check_code_errors, detect_language

logger = logging.getLogger(__name__)

@api_bp.route('/check_errors', methods=['POST'])
def check_errors():
    """
    Check code for errors and provide suggestions using Cloudflare AI
    
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
    
    # Если язык не указан, определяем его
    if language not in Config.SUPPORTED_LANGUAGES:
        detected_language = detect_language(code)
        if detected_language in Config.SUPPORTED_LANGUAGES:
            language = detected_language
            logger.info(f"Using detected language: {language}")
        else:
            return jsonify({
                "error": f"Unsupported language. Supported languages are: {', '.join(Config.SUPPORTED_LANGUAGES)}"
            }), 400
    
    try:
        logger.debug(f"Processing error check request for language {language}")
        
        start_time = time.time()
        
        # Используем Cloudflare AI для проверки кода на ошибки
        result = check_code_errors(code, language)
        
        # Расчитываем время обработки
        processing_time = time.time() - start_time
        
        # Преобразуем результат в ожидаемый формат ответа
        response = {
            "errors": result.get("errors", []),
            "suggestions": result.get("suggestions", []),
            "corrected_code": result.get("corrected_code", code),
            "language": language,
            "input_code": code,
            "processing_time": processing_time,
            "demo_mode": False
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in error checking: {str(e)}")
        return jsonify({"error": f"Error checking failed: {str(e)}"}), 500
