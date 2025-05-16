"""
API для тестирования функциональности системы в браузере
"""

import logging
from flask import request, jsonify, render_template
from api import api_bp
from brain.cloudflare_ai import get_ai_thinking, get_code_completion, check_code_errors, detect_language
from brain.web_access import get_webpage_content, search_programming_solutions

logger = logging.getLogger(__name__)

@api_bp.route('/try/ai-thinking', methods=['GET'])
def try_ai_thinking():
    """Страница для тестирования функции AI Thinking"""
    return render_template('try_api/ai_thinking.html')

@api_bp.route('/try/code-completion', methods=['GET'])
def try_code_completion():
    """Страница для тестирования функции Code Completion"""
    return render_template('try_api/code_completion.html')

@api_bp.route('/try/error-checking', methods=['GET'])
def try_error_checking():
    """Страница для тестирования функции Error Checking"""
    return render_template('try_api/error_checking.html')

@api_bp.route('/try/language-detection', methods=['GET'])
def try_language_detection():
    """Страница для тестирования функции Language Detection"""
    return render_template('try_api/language_detection.html')

@api_bp.route('/try/web-search', methods=['GET'])
def try_web_search():
    """Страница для тестирования функции Web Search"""
    return render_template('try_api/web_search.html')

@api_bp.route('/try/web-content', methods=['GET'])
def try_web_content():
    """Страница для тестирования функции Web Content"""
    return render_template('try_api/web_content.html')

@api_bp.route('/try/all-features', methods=['GET'])
def try_all_features():
    """Страница для тестирования всех функций"""
    return render_template('try_api/all_features.html')