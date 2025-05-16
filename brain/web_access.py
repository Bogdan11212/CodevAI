"""
Модуль для доступа к интернету и получения данных для обучения ИИ
"""

import requests
import logging
import traceback
import trafilatura
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def is_valid_url(url):
    """
    Проверяет, является ли строка допустимым URL
    
    Args:
        url (str): URL для проверки
        
    Returns:
        bool: True, если URL валидный
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_webpage_content(url):
    """
    Получает содержимое веб-страницы по URL
    
    Args:
        url (str): URL веб-страницы
        
    Returns:
        str: Текстовое содержимое страницы или None в случае ошибки
    """
    if not is_valid_url(url):
        logger.error(f"Недопустимый URL: {url}")
        return None
    
    try:
        # Используем trafilatura для извлечения чистого текста
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        else:
            logger.error(f"Не удалось загрузить страницу: {url}")
            return None
    except Exception as e:
        logger.error(f"Ошибка при получении содержимого страницы {url}: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def search_programming_solutions(query, language=None):
    """
    Выполняет поиск решений по программированию
    
    Args:
        query (str): Поисковый запрос
        language (str, optional): Язык программирования
        
    Returns:
        list: Список найденных решений
    """
    # В реальной системе здесь был бы код для поиска через API
    # или парсинга результатов поисковой выдачи
    
    # Этот пример демонстрирует концепцию
    try:
        search_query = query
        if language:
            search_query += f" {language} programming"
            
        # Здесь можно добавить код для интеграции с поисковыми API или другими источниками
        
        # Заглушка для демо
        return [
            {
                "title": f"Solution for {query} in {language or 'any language'}",
                "description": "This is a placeholder for real search results",
                "url": f"https://example.com/search?q={query}"
            }
        ]
    except Exception as e:
        logger.error(f"Ошибка при поиске решений: {str(e)}")
        logger.debug(traceback.format_exc())
        return []

def get_programming_resources(language):
    """
    Получает ресурсы по программированию для указанного языка
    
    Args:
        language (str): Язык программирования
        
    Returns:
        list: Список ресурсов
    """
    resources = {
        "python": [
            {"name": "Python Documentation", "url": "https://docs.python.org/3/"},
            {"name": "Real Python", "url": "https://realpython.com/"},
            {"name": "Python.org", "url": "https://www.python.org/"}
        ],
        "javascript": [
            {"name": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"},
            {"name": "JavaScript.info", "url": "https://javascript.info/"},
            {"name": "ECMAScript Specification", "url": "https://tc39.es/ecma262/"}
        ],
        "java": [
            {"name": "Oracle Java Documentation", "url": "https://docs.oracle.com/en/java/"},
            {"name": "Baeldung", "url": "https://www.baeldung.com/"},
            {"name": "Java Code Geeks", "url": "https://www.javacodegeeks.com/"}
        ],
        "cpp": [
            {"name": "CPlusPlus.com", "url": "https://cplusplus.com/"},
            {"name": "C++ Reference", "url": "https://en.cppreference.com/w/"},
            {"name": "ISO C++ Standard", "url": "https://isocpp.org/std/the-standard"}
        ]
    }
    
    return resources.get(language.lower(), [])