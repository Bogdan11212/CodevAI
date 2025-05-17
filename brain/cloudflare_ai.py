"""
Module for working with Cloudflare AI and other Cloudflare services

This module provides access to Cloudflare AI models and other Cloudflare services:
- Text generation and completion with Llama 3
- Code analysis and generation
- Image recognition and analysis
- Content moderation
- And other Cloudflare Workers AI capabilities
"""

import os
import requests
import json
import logging
import time
import traceback
import base64
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Check for Cloudflare AI token and account ID
CLOUDFLARE_AI_TOKEN = os.environ.get("CLOUDFLARE_AI_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

# Log warning if tokens not found
if not CLOUDFLARE_AI_TOKEN:
    logger.warning("Cloudflare AI token not found. A valid token is required for real-time operation.")
if not CLOUDFLARE_ACCOUNT_ID:
    logger.warning("Cloudflare Account ID not found. This is required for accessing Cloudflare services.")

# Base URLs for Cloudflare services
CLOUDFLARE_AI_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"

# Available models
MODELS = {
    "llama3-8b": "@cf/meta/llama-3-8b-instruct",
    "llama3-70b": "@cf/meta/llama-3-70b-instruct",
    "claude-instant": "@cf/anthropic/claude-instant-1",
    "claude-2": "@cf/anthropic/claude-2",
    "stable-diffusion": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "moderation": "@cf/cloudflare/moderation",
    "image-classification": "@cf/microsoft/resnet-50"
}

def get_ai_thinking(prompt, language="general", max_thoughts=3):
    """
    Обрабатывает запрос, используя Cloudflare AI Workers
    
    Args:
        prompt (str): Запрос пользователя
        language (str): Язык программирования
        max_thoughts (int): Максимальное количество мыслей
        
    Returns:
        dict: Результат обработки с мыслями, комментариями и ответом
    """
    if not CLOUDFLARE_AI_TOKEN:
        # Если токен не предоставлен, используем локальный режим шаблонов
        return get_fallback_thinking(prompt, language, max_thoughts)
    
    try:
        # Формируем системный промпт для размышлений
        system_message = f"""Вы опытный разработчик на {language}. 
        Проанализируйте следующий запрос, размышляя вслух о решении.
        Ваш ответ должен включать:

        1. Несколько этапов размышлений (в формате список)
        2. Несколько технических комментариев к вашему подходу (в формате список)
        3. Окончательный ответ в виде кода или объяснения

        Ответ должен быть в формате JSON:
        {{
          "thoughts": [
            {{"thought": "Первая мысль о подходе к решению", "timestamp": 1620000000}},
            {{"thought": "Вторая мысль", "timestamp": 1620000001}}
          ],
          "comments": [
            "Технический комментарий 1",
            "Технический комментарий 2"
          ],
          "answer": "Ваш финальный ответ в виде текста или кода"
        }}
        """
        
        # Подготавливаем параметры запроса для @cf/meta/llama-3-8b-instruct
        url = f"{CLOUDFLARE_AI_URL}@cf/meta/llama-3-8b-instruct"
        url = url.replace("{account_id}", CLOUDFLARE_ACCOUNT_ID)
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_AI_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            logger.error(f"Ошибка при запросе к Cloudflare AI Workers: {response.status_code} - {response.text}")
            return get_fallback_thinking(prompt, language, max_thoughts)
        
        # Парсим ответ
        response_data = response.json()
        result_text = response_data.get("result", {}).get("response", "")
        
        # Пытаемся извлечь JSON из текстового ответа
        try:
            # Извлекаем JSON из текста (может быть обернут в markdown блоки)
            if "```json" in result_text:
                json_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_text = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = result_text
            
            result = json.loads(json_text)
        except Exception as e:
            logger.error(f"Ошибка при парсинге JSON ответа: {str(e)}")
            
            # Если не удалось распарсить JSON, создаем базовую структуру
            result = {
                "thoughts": [
                    {"thought": "Анализ запроса...", "timestamp": time.time()},
                    {"thought": "Обработка инструкций...", "timestamp": time.time() + 1}
                ],
                "comments": ["Не удалось получить структурированный ответ"],
                "answer": result_text
            }
        
        # Ограничиваем количество мыслей
        if "thoughts" in result and len(result["thoughts"]) > max_thoughts:
            result["thoughts"] = result["thoughts"][:max_thoughts]
            
        # Убедимся, что у всех мыслей есть timestamp
        for thought in result.get("thoughts", []):
            if "timestamp" not in thought:
                thought["timestamp"] = time.time()
            
        # Добавляем метаданные
        result["language"] = language
        result["prompt"] = prompt
        result["processing_time"] = time.time() - start_time
        
        return result
            
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса через Cloudflare AI: {str(e)}")
        logger.debug(traceback.format_exc())
        # Возвращаемся к шаблонным ответам в случае ошибки
        return get_fallback_thinking(prompt, language, max_thoughts)

def get_code_completion(code_snippet, language, max_tokens=500):
    """
    Генерирует завершение кода с использованием Cloudflare AI
    
    Args:
        code_snippet (str): Фрагмент кода для завершения
        language (str): Язык программирования
        max_tokens (int): Максимальное количество токенов
        
    Returns:
        str: Завершенный код
    """
    if not CLOUDFLARE_AI_TOKEN:
        # Шаблонное завершение кода при отсутствии токена
        return f"{code_snippet}\n    # Шаблонное завершение кода\n    pass"
    
    try:
        system_message = f"""Вы опытный программист на {language}. 
        Завершите следующий фрагмент кода логично и в соответствии с лучшими практиками.
        Возвращайте только код, без объяснений."""
        
        # Подготавливаем параметры запроса
        url = f"{CLOUDFLARE_AI_URL}@cf/meta/llama-3-8b-instruct"
        url = url.replace("{account_id}", CLOUDFLARE_ACCOUNT_ID)
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_AI_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": code_snippet}
            ],
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            logger.error(f"Ошибка при запросе к Cloudflare AI Workers: {response.status_code} - {response.text}")
            return f"{code_snippet}\n    # Ошибка при получении ответа от Cloudflare AI\n    pass"
        
        # Парсим ответ
        response_data = response.json()
        result_text = response_data.get("result", {}).get("response", "")
        
        # Извлекаем код из ответа (может быть обернут в markdown блоки)
        if "```" in result_text:
            # Извлекаем блок кода
            code_blocks = result_text.split("```")
            if len(code_blocks) > 1:
                # Берем первый блок кода, игнорируя язык, если он указан
                code_block = code_blocks[1]
                if code_block.split("\n")[0] in [language, "python", "javascript", "java", "cpp"]:
                    code_block = "\n".join(code_block.split("\n")[1:])
                return code_block.strip()
        
        # Если нет маркеров кода, возвращаем весь текст
        return result_text
        
    except Exception as e:
        logger.error(f"Ошибка при завершении кода: {str(e)}")
        logger.debug(traceback.format_exc())
        # Шаблонное завершение кода при ошибке
        return f"{code_snippet}\n    # Ошибка API при завершении кода\n    pass"

def check_code_errors(code, language):
    """
    Проверяет код на наличие ошибок и предлагает исправления
    
    Args:
        code (str): Код для проверки
        language (str): Язык программирования
        
    Returns:
        dict: Результаты проверки с ошибками и предложениями
    """
    if not CLOUDFLARE_AI_TOKEN:
        # Шаблонный ответ при отсутствии токена
        return {
            "has_errors": False,
            "errors": [],
            "suggestions": ["Нет доступных предложений без Cloudflare AI токена"]
        }
    
    try:
        system_message = f"""Вы опытный программист на {language}. 
        Проверьте следующий код на наличие синтаксических ошибок, логических ошибок и стилевых проблем.
        Верните результаты проверки в формате JSON:
        {{
          "has_errors": true,
          "errors": [
            {{"line": 5, "description": "Описание ошибки", "severity": "error|warning|info"}},
            ...
          ],
          "suggestions": [
            "Предложение по улучшению кода 1",
            ...
          ],
          "corrected_code": "Исправленный код (если есть ошибки)"
        }}
        """
        
        # Подготавливаем параметры запроса
        url = f"{CLOUDFLARE_AI_URL}@cf/meta/llama-3-8b-instruct"
        url = url.replace("{account_id}", CLOUDFLARE_ACCOUNT_ID)
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_AI_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": code}
            ],
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            logger.error(f"Ошибка при запросе к Cloudflare AI Workers: {response.status_code} - {response.text}")
            return {
                "has_errors": False,
                "errors": [],
                "suggestions": ["Ошибка при получении ответа от Cloudflare AI"]
            }
        
        # Парсим ответ
        response_data = response.json()
        result_text = response_data.get("result", {}).get("response", "")
        
        # Пытаемся извлечь JSON из текстового ответа
        try:
            # Извлекаем JSON из текста (может быть обернут в markdown блоки)
            if "```json" in result_text:
                json_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_text = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = result_text
            
            result = json.loads(json_text)
            return result
        except Exception as json_e:
            logger.error(f"Ошибка при парсинге JSON ответа: {str(json_e)}")
            return {
                "has_errors": False,
                "errors": [],
                "suggestions": ["Не удалось получить структурированный ответ"],
                "raw_response": result_text
            }
        
    except Exception as e:
        logger.error(f"Ошибка при проверке кода: {str(e)}")
        logger.debug(traceback.format_exc())
        # Шаблонный ответ при ошибке
        return {
            "has_errors": False,
            "errors": [],
            "suggestions": ["Ошибка API при проверке кода"]
        }

def detect_language(code):
    """
    Определяет язык программирования по коду
    
    Args:
        code (str): Код для анализа
        
    Returns:
        str: Определенный язык программирования
    """
    if not CLOUDFLARE_AI_TOKEN:
        # Шаблонное определение языка при отсутствии токена
        if "def " in code and ":" in code:
            return "python"
        elif "function" in code and "{" in code:
            return "javascript"
        else:
            return "unknown"
    
    try:
        system_message = """Определите язык программирования для следующего кода.
        Верните только название языка в нижнем регистре (например, "python", "javascript", "java", "cpp", "rust").
        """
        
        # Подготавливаем параметры запроса
        url = f"{CLOUDFLARE_AI_URL}@cf/meta/llama-3-8b-instruct"
        url = url.replace("{account_id}", CLOUDFLARE_ACCOUNT_ID)
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_AI_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": code}
            ],
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            logger.error(f"Ошибка при запросе к Cloudflare AI Workers: {response.status_code} - {response.text}")
            # В случае ошибки используем простое определение
            if "def " in code and ":" in code:
                return "python"
            elif "function" in code and "{" in code:
                return "javascript"
            else:
                return "unknown"
        
        # Парсим ответ
        response_data = response.json()
        result_text = response_data.get("result", {}).get("response", "").strip().lower()
        
        # Проверяем, что ответ является одним из известных языков
        known_languages = ["python", "javascript", "java", "cpp", "rust", "go", "php", "ruby", "c#", "typescript"]
        
        for language in known_languages:
            if language in result_text:
                return language
                
        # Если не смогли определить язык из ответа, возвращаем первое слово
        first_word = result_text.split()[0] if result_text else "unknown"
        return first_word
        
    except Exception as e:
        logger.error(f"Ошибка при определении языка: {str(e)}")
        logger.debug(traceback.format_exc())
        # Шаблонное определение языка при ошибке
        if "def " in code and ":" in code:
            return "python"
        elif "function" in code and "{" in code:
            return "javascript"
        else:
            return "unknown"

def get_fallback_thinking(prompt, language, max_thoughts):
    """
    Генерирует шаблонный ответ, имитирующий мыслительный процесс ИИ
    Используется при отсутствии доступа к API
    
    Args:
        prompt (str): Запрос пользователя
        language (str): Язык программирования
        max_thoughts (int): Максимальное количество мыслей
        
    Returns:
        dict: Шаблонный ответ с имитацией мыслительного процесса
    """
    import random
    from brain.thinking_patterns import get_thinking_pattern, get_thinking_comments
    
    # Получаем шаблоны мышления и комментарии
    patterns = get_thinking_pattern(language)
    comments = get_thinking_comments(language)
    
    # Генерируем случайные мысли
    thoughts = []
    used_patterns = set()
    
    for _ in range(min(max_thoughts, len(patterns))):
        available_patterns = [p for p in patterns if p not in used_patterns]
        if not available_patterns:
            break
            
        thought = random.choice(available_patterns)
        used_patterns.add(thought)
        
        thoughts.append({
            "thought": thought,
            "timestamp": time.time()
        })
    
    # Генерируем случайные комментарии
    selected_comments = []
    used_comments = set()
    
    for _ in range(min(2, len(comments))):
        available_comments = [c for c in comments if c not in used_comments]
        if not available_comments:
            break
            
        comment = random.choice(available_comments)
        used_comments.add(comment)
        
        selected_comments.append(comment)
    
    # Шаблонные ответы по языкам
    answers = {
        "python": """def process_request(prompt):
    # Обрабатывает пользовательский запрос и возвращает ответ
    # Анализируем запрос
    keywords = prompt.lower().split()
    
    # Проверяем требования
    if any(word in keywords for word in ["пример", "образец", "демо"]):
        return "Вот пример решения на Python: ..."
    
    # Генерируем ответ
    response = "Решение на Python для запроса: " + prompt
    return response

# Пример использования
print(process_request("Ваш запрос"))""",
        
        "javascript": """function processRequest(prompt) {
  // Обрабатывает пользовательский запрос и возвращает ответ
  
  // Анализируем запрос
  const keywords = prompt.toLowerCase().split(' ');
  
  // Проверяем требования
  if (keywords.some(word => ["пример", "образец", "демо"].includes(word))) {
    return "Вот пример решения на JavaScript: ...";
  }
  
  // Генерируем ответ
  const response = "Решение на JavaScript для запроса: " + prompt;
  return response;
}

// Пример использования
console.log(processRequest("Ваш запрос"));""",
        
        "general": """// Функция для обработки запроса
function processRequest(input) {
  // Анализируем входные данные
  // Применяем алгоритм
  // Возвращаем результат
  return "Ответ на запрос: " + input;
}"""
    }
    
    final_answer = answers.get(language, answers["general"])
    
    # Готовим ответ с имитацией задержки "размышления"
    response = {
        "thoughts": thoughts,
        "comments": selected_comments,
        "answer": final_answer,
        "processing_time": random.uniform(0.5, 2.0),
        "language": language,
        "prompt": prompt,
        "is_fallback": True
    }
    
    return response