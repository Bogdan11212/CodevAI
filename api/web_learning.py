"""
API для управления системой непрерывного обучения CodevAI через веб-интерфейс
"""

import logging
import json
from flask import request, jsonify
from api import api_bp
from web_scraper import enqueue_url_for_learning, process_url_now, get_website_text_content
from brain.continuous_learning import count_knowledge_items, knowledge_base

logger = logging.getLogger(__name__)

@api_bp.route('/learning/enqueue', methods=['POST'])
def api_enqueue_url():
    """
    Добавляет URL в очередь для обработки системой непрерывного обучения
    
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
    
    # Добавляем URL в очередь для обработки
    success = enqueue_url_for_learning(url)
    
    if success:
        return jsonify({"success": True, "message": "URL успешно добавлен в очередь"}), 200
    else:
        return jsonify({"success": False, "error": "Не удалось добавить URL в очередь"}), 400

@api_bp.route('/learning/process', methods=['POST'])
def api_process_url():
    """
    Немедленно обрабатывает URL для извлечения знаний
    
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
    
    # Обрабатываем URL немедленно
    result = process_url_now(url)
    
    return jsonify(result), 200 if result.get("success", False) else 400

@api_bp.route('/learning/content', methods=['POST'])
def api_get_url_content():
    """
    Получает содержимое веб-страницы
    
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
    
    # Получаем содержимое веб-страницы
    content = get_website_text_content(url)
    
    return jsonify({"content": content}), 200

@api_bp.route('/learning/status', methods=['GET'])
def api_learning_status():
    """
    Получает статус системы непрерывного обучения
    """
    try:
        # Получаем информацию о базе знаний
        item_count = count_knowledge_items()
        last_updated = knowledge_base.get("last_updated", "Never")
        
        # Формируем статус по категориям
        categories_status = {}
        for category in knowledge_base:
            if category != "last_updated":
                categories_status[category] = len(knowledge_base[category])
        
        return jsonify({
            "status": "active",
            "total_items": item_count,
            "last_updated": last_updated,
            "categories": categories_status
        }), 200
    except Exception as e:
        logger.error(f"Ошибка при получении статуса системы обучения: {str(e)}")
        return jsonify({"error": "Не удалось получить статус системы обучения"}), 500