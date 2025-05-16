"""
Основной модуль для обработки запросов с использованием OpenAI API
"""

import os
import logging
import traceback
import json
import time
from openai import OpenAI
from brain.thinking_patterns import get_thinking_pattern, get_thinking_comments

logger = logging.getLogger(__name__)

# Проверяем наличие API ключа
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OpenAI API ключ не найден. Будут использоваться шаблонные ответы.")

# Инициализация клиента OpenAI
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception as e:
    logger.error(f"Ошибка при инициализации OpenAI API: {str(e)}")
    openai_client = None

def get_ai_thinking(prompt, language="general", max_thoughts=3):
    """
    Обрабатывает запрос, используя настоящий мыслительный процесс ИИ
    
    Args:
        prompt (str): Запрос пользователя
        language (str): Язык программирования
        max_thoughts (int): Максимальное количество мыслей
        
    Returns:
        dict: Результат обработки с мыслями, комментариями и ответом
    """
    # Если API не доступен, используем шаблонные ответы
    if not openai_client:
        return get_fallback_thinking(prompt, language, max_thoughts)
    
    try:
        # Формируем системный промпт для размышлений
        system_prompt = f"""Вы опытный разработчик на {language}. 
        Проанализируйте следующий запрос, размышляя вслух о решении.
        Ваш ответ должен включать:

        1. Несколько этапов размышлений (в формате список)
        2. Несколько технических комментариев к вашему подходу (в формате список)
        3. Окончательный ответ в виде кода или объяснения

        Ответ должен быть в формате JSON:
        {
          "thoughts": [
            {"thought": "Первая мысль о подходе к решению", "timestamp": unix_timestamp},
            {"thought": "Вторая мысль", "timestamp": unix_timestamp}
          ],
          "comments": [
            "Технический комментарий 1",
            "Технический комментарий 2"
          ],
          "answer": "Ваш финальный ответ в виде текста или кода"
        }
        """
        
        # Запрос к OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500
        )
        
        # Парсим ответ из JSON
        result = json.loads(response.choices[0].message.content)
        
        # Ограничиваем количество мыслей
        if len(result["thoughts"]) > max_thoughts:
            result["thoughts"] = result["thoughts"][:max_thoughts]
            
        # Добавляем метаданные
        result["language"] = language
        result["prompt"] = prompt
        result["processing_time"] = response.usage.total_tokens / 100  # Приблизительное время обработки
        
        return result
            
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса через OpenAI: {str(e)}")
        logger.debug(traceback.format_exc())
        # Возвращаемся к шаблонным ответам в случае ошибки
        return get_fallback_thinking(prompt, language, max_thoughts)
        
def get_code_completion(code_snippet, language, max_tokens=500):
    """
    Генерирует завершение кода с использованием OpenAI API
    
    Args:
        code_snippet (str): Фрагмент кода для завершения
        language (str): Язык программирования
        max_tokens (int): Максимальное количество токенов
        
    Returns:
        str: Завершенный код
    """
    if not openai_client:
        # Шаблонное завершение кода при отсутствии API
        return f"{code_snippet}\n    # Шаблонное завершение кода\n    pass"
    
    try:
        system_prompt = f"""Вы опытный программист на {language}. 
        Завершите следующий фрагмент кода логично и в соответствии с лучшими практиками.
        Возвращайте только код, без объяснений."""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code_snippet}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
        
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
    if not openai_client:
        # Шаблонный ответ при отсутствии API
        return {
            "has_errors": False,
            "errors": [],
            "suggestions": ["Нет доступных предложений без API"]
        }
    
    try:
        system_prompt = f"""Вы опытный программист на {language}. 
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
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000
        )
        
        return json.loads(response.choices[0].message.content)
        
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
    if not openai_client:
        # Шаблонное определение языка при отсутствии API
        if "def " in code and ":" in code:
            return "python"
        elif "function" in code and "{" in code:
            return "javascript"
        else:
            return "unknown"
    
    try:
        system_prompt = """Определите язык программирования для следующего кода.
        Верните только название языка в нижнем регистре (например, "python", "javascript", "java", "cpp", "rust").
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code}
            ],
            temperature=0.1,
            max_tokens=20
        )
        
        language = response.choices[0].message.content.strip().lower()
        return language
        
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