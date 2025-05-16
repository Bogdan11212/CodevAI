"""
Module for internet access and retrieving data for AI training
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
        logger.error(f"Invalid URL: {url}")
        return None
    
    try:
        # Use trafilatura to extract clean text content
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        else:
            logger.error(f"Failed to load page: {url}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving content from page {url}: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def search_programming_solutions(query, language=None):
    """
    Performs search for programming solutions using various sources
    
    Args:
        query (str): Search query
        language (str, optional): Programming language
        
    Returns:
        list: List of found solutions
    """
    try:
        search_query = query
        if language:
            search_query += f" {language} programming"
            
        # List of programming-focused domains to search
        domains = [
            "stackoverflow.com",
            "github.com",
            "dev.to",
            "medium.com/programming",
            "realpython.com",
            "javascript.info",
            "python.org/doc"
        ]
        
        results = []
        
        for domain in domains:
            # Form search URL for each domain
            if domain == "stackoverflow.com":
                url = f"https://stackoverflow.com/search?q={search_query}"
            elif domain == "github.com":
                url = f"https://github.com/search?q={search_query}&type=repositories"
            else:
                url = f"https://{domain}/search?q={search_query}"
                
            # Get content from each URL
            content = get_webpage_content(url)
            if content:
                results.append({
                    "title": f"Results from {domain}",
                    "description": content[:200] + "...",
                    "url": url,
                    "source": domain
                })
                
        return results
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