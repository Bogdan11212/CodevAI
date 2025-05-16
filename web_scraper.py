"""
Web Scraper для CodevAI

Этот модуль предоставляет функциональность для извлечения и обработки содержимого
веб-страниц для системы обучения ИИ CodevAI.
"""

import logging
import trafilatura
from brain.continuous_learning import add_url_to_queue, process_url
from brain.web_access import is_valid_url

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    Эта функция берет URL и возвращает основное текстовое содержимое веб-сайта.
    Текстовое содержимое извлекается с помощью trafilatura и легче для понимания.
    Результаты не предназначены для прямого чтения, лучше их обобщать через LLM
    перед использованием.

    Некоторые популярные сайты для получения информации:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    if not is_valid_url(url):
        logger.error(f"Недопустимый URL: {url}")
        return "Ошибка: Недопустимый URL"
    
    try:
        # Отправляем запрос на веб-сайт
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.error(f"Не удалось загрузить страницу: {url}")
            return "Ошибка: Не удалось загрузить страницу"
        
        # Извлекаем текстовое содержимое
        text = trafilatura.extract(downloaded)
        
        # Добавляем URL в очередь на обучение
        add_url_to_queue(url)
        
        return text if text else "Не удалось извлечь содержимое"
    except Exception as e:
        logger.error(f"Ошибка при получении содержимого веб-страницы {url}: {str(e)}")
        return f"Ошибка при обработке URL: {str(e)}"

def enqueue_url_for_learning(url: str) -> bool:
    """
    Добавляет URL в очередь для обработки системой непрерывного обучения
    
    Args:
        url (str): URL для добавления
        
    Returns:
        bool: True если URL был добавлен успешно, иначе False
    """
    if not is_valid_url(url):
        logger.error(f"Недопустимый URL для обучения: {url}")
        return False
    
    return add_url_to_queue(url)

def process_url_now(url: str) -> dict:
    """
    Немедленно обрабатывает URL для извлечения знаний
    
    Args:
        url (str): URL для обработки
        
    Returns:
        dict: Результат обработки или None в случае ошибки
    """
    if not is_valid_url(url):
        logger.error(f"Недопустимый URL для немедленной обработки: {url}")
        return {"success": False, "error": "Недопустимый URL"}
    
    success = process_url(url)
    if success:
        return {"success": True, "message": "URL успешно обработан"}
    else:
        return {"success": False, "error": "Не удалось обработать URL"}