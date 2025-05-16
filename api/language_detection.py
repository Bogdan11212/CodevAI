import logging
import time
from flask import request, jsonify
from api import api_bp
from config import Config
from brain.cloudflare_ai import detect_language

logger = logging.getLogger(__name__)

@api_bp.route('/detect_language', methods=['POST'])
def detect_language_api():
    """
    Detect the programming language of the provided code using Cloudflare AI
    
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
        logger.debug("Processing language detection request")
        
        start_time = time.time()
        
        # Используем Cloudflare AI для определения языка
        detected_language = detect_language(code)
        
        # Расчитываем время обработки
        processing_time = time.time() - start_time
        
        # Check if detected language is in our supported list
        supported = detected_language in Config.SUPPORTED_LANGUAGES
        
        logger.debug(f"Detected language: {detected_language}, supported: {supported}")
        
        # Определяем уровень уверенности на основе длины кода
        # В реальности это значение должно приходить от модели
        if len(code) > 100:
            confidence = 0.95
        elif len(code) > 50:
            confidence = 0.9
        else:
            confidence = 0.85
        
        # Prepare response
        response = {
            "detected_language": detected_language,
            "supported": supported,
            "confidence": confidence,
            "processing_time": processing_time,
            "demo_mode": False
        }
        
        if not supported:
            response["supported_languages"] = Config.SUPPORTED_LANGUAGES
            
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in language detection: {str(e)}")
        return jsonify({"error": f"Language detection failed: {str(e)}"}), 500
