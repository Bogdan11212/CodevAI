import logging
import time
import json
import os
from flask import request, jsonify
from api import api_bp
from brain.ai_processor import get_ai_thinking
from brain.web_access import get_webpage_content, search_programming_solutions

logger = logging.getLogger(__name__)

@api_bp.route('/ai-thinking', methods=['POST'])
def ai_thinking():
    """
    Использует настоящий AI для размышления над запросом и формирования ответа
    
    Ожидаемый JSON запрос:
    {
        "prompt": "Напиши код функции, которая находит наибольший общий делитель двух чисел",
        "language": "python",
        "max_thoughts": 5   // необязательно, по умолчанию 3
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Данные не предоставлены"}), 400
    
    prompt = data.get('prompt')
    language = data.get('language', 'general').lower()
    max_thoughts = data.get('max_thoughts', 3)
    
    if not prompt:
        return jsonify({"error": "Запрос не предоставлен"}), 400
    
    # Проверяем наличие API ключа OpenAI
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OpenAI API ключ не найден. Для работы в реальном режиме необходим действительный ключ.")
    
    # Используем модуль реального мышления ИИ вместо заготовленных шаблонов
    response = get_ai_thinking(prompt, language, max_thoughts)
    
    return jsonify(response), 200

@api_bp.route('/web-search', methods=['POST'])
def web_search():
    """
    Выполняет поиск программистских решений в Интернете
    
    Ожидаемый JSON запрос:
    {
        "query": "Python рекурсивная сортировка",
        "language": "python"  // необязательно
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Данные не предоставлены"}), 400
    
    query = data.get('query')
    language = data.get('language')
    
    if not query:
        return jsonify({"error": "Поисковый запрос не предоставлен"}), 400
    
    # Выполняем поиск решений
    results = search_programming_solutions(query, language)
    
    return jsonify({"results": results}), 200

@api_bp.route('/web-content', methods=['POST'])
def web_content():
    """
    Получает содержимое веб-страницы для обучения ИИ
    
    Ожидаемый JSON запрос:
    {
        "url": "https://example.com/python-tutorial"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Данные не предоставлены"}), 400
    
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL не предоставлен"}), 400
    
    # Получаем содержимое страницы
    content = get_webpage_content(url)
    
    if not content:
        return jsonify({"error": "Не удалось получить содержимое страницы"}), 400
    
    return jsonify({"content": content}), 200