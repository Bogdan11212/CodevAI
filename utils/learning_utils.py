import logging
import json
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
from utils.model_utils import update_model_weights, get_language_model_version
from models import Feedback, ModelVersion, db, CodeExample
from config import Config

logger = logging.getLogger(__name__)

# Store feedback counts for tracking when to trigger learning
feedback_counts = defaultdict(int)

# Симуляция улучшений модели
model_improvement_stats = {
    "iterations": 0,
    "last_updated": datetime.utcnow(),
    "improvements": [],
    "total_samples_processed": 0
}

# Список примеров кода для обучения модели
training_examples = [
    {
        "language": "python",
        "code_input": "def fibonacci(n):",
        "expected_output": "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
        "feedback_type": "completion",
        "rating": 5
    },
    {
        "language": "python", 
        "code_input": "def quicksort(arr):",
        "expected_output": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)",
        "feedback_type": "completion",
        "rating": 4
    },
    {
        "language": "javascript",
        "code_input": "function fibonacci(n) {",
        "expected_output": "function fibonacci(n) {\n  if (n <= 0) return 0;\n  if (n === 1) return 1;\n  return fibonacci(n-1) + fibonacci(n-2);\n}",
        "feedback_type": "completion",
        "rating": 5
    },
]

def continuous_learning_task():
    """
    Функция постоянного обучения модели, запускается в отдельном потоке.
    Симулирует обучение модели на основе накопленных данных и генерирует отчеты об улучшении.
    """
    logger.info("Continuous learning task started")
    
    # Интервал в секундах между итерациями обучения
    learning_interval = 10
    
    # Количество примеров, добавляемых для обучения в каждой итерации
    examples_per_iteration = 3
    
    # Максимальное улучшение точности в каждой итерации (в процентах)
    max_accuracy_improvement = 0.5
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            logger.info(f"Starting learning iteration {iteration}")
            
            # Симуляция процесса обучения
            processed_examples = []
            
            # Выбор случайных примеров из базы для обучения
            for _ in range(examples_per_iteration):
                example = random.choice(training_examples)
                processed_examples.append(example)
                
            # Симуляция улучшения модели
            accuracy_improvement = random.uniform(0.1, max_accuracy_improvement)
            
            # Создание нового примера кода на основе обучения
            new_example = create_new_code_example()
            
            # Обновление статистики модели
            model_improvement_stats["iterations"] = iteration
            model_improvement_stats["last_updated"] = datetime.utcnow()
            model_improvement_stats["total_samples_processed"] += len(processed_examples)
            model_improvement_stats["improvements"].append({
                "iteration": iteration,
                "timestamp": datetime.utcnow().isoformat(),
                "accuracy_improvement": accuracy_improvement,
                "samples_processed": len(processed_examples),
                "new_example_created": new_example.id if new_example else None
            })
            
            # Создание записи о новой версии модели
            try:
                # Мы используем имеющийся контекст приложения вместо создания нового
                new_version = f"0.1.{iteration}"
                
                # Параметры модели
                parameters = {
                    "learning_rate": Config.LEARNING_RATE,
                    "examples_processed": model_improvement_stats["total_samples_processed"],
                    "training_languages": list(set(ex["language"] for ex in processed_examples))
                }
                
                # Метрики производительности
                metrics = {
                    "accuracy_improvement": accuracy_improvement,
                    "total_iterations": iteration,
                    "last_processed_languages": list(set(ex["language"] for ex in processed_examples))
                }
                
                # Использование простой записи в словарь вместо базы данных для этой демо версии
                # В реальном приложении здесь был бы нормальный код работы с базой данных
                model_improvement_stats["last_model_version"] = {
                    "version": new_version,
                    "description": f"Automatically improved model after iteration {iteration}",
                    "parameters": parameters,
                    "performance_metrics": metrics
                }
                
                logger.info(f"New model version created: {new_version} with accuracy improvement: {accuracy_improvement:.2f}%")
            except Exception as e:
                logger.error(f"Error creating model version: {str(e)}")
            
            # Ожидание до следующей итерации
            time.sleep(learning_interval)
            
    except Exception as e:
        logger.error(f"Error in continuous learning task: {str(e)}")
        
def create_new_code_example():
    """
    Создает новый пример кода на основе обучения модели
    Для демо-версии просто возвращает информацию о примере, не сохраняя в БД
    """
    try:
        # Список возможных категорий примеров кода
        categories = ["algorithm", "data-structure", "utility", "pattern"]
        
        # Список возможных языков
        languages = Config.SUPPORTED_LANGUAGES
        
        # Генерация случайного примера кода
        language = random.choice(languages)
        category = random.choice(categories)
        
        code_snippets = {
            "python": {
                "algorithm": "def merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] < right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result",
                "data-structure": "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\nclass BinarySearchTree:\n    def __init__(self):\n        self.root = None\n        \n    def insert(self, val):\n        if not self.root:\n            self.root = TreeNode(val)\n            return\n        self._insert_recursive(self.root, val)\n        \n    def _insert_recursive(self, node, val):\n        if val < node.val:\n            if node.left is None:\n                node.left = TreeNode(val)\n            else:\n                self._insert_recursive(node.left, val)\n        else:\n            if node.right is None:\n                node.right = TreeNode(val)\n            else:\n                self._insert_recursive(node.right, val)",
            },
            "javascript": {
                "algorithm": "function mergeSort(arr) {\n  if (arr.length <= 1) return arr;\n  \n  const mid = Math.floor(arr.length / 2);\n  const left = mergeSort(arr.slice(0, mid));\n  const right = mergeSort(arr.slice(mid));\n  \n  return merge(left, right);\n}\n\nfunction merge(left, right) {\n  let result = [];\n  let i = 0, j = 0;\n  \n  while (i < left.length && j < right.length) {\n    if (left[i] < right[j]) {\n      result.push(left[i]);\n      i++;\n    } else {\n      result.push(right[j]);\n      j++;\n    }\n  }\n  \n  return [...result, ...left.slice(i), ...right.slice(j)];\n}",
                "utility": "function debounce(func, wait, immediate) {\n  let timeout;\n  \n  return function executedFunction() {\n    const context = this;\n    const args = arguments;\n    \n    const later = function() {\n      timeout = null;\n      if (!immediate) func.apply(context, args);\n    };\n    \n    const callNow = immediate && !timeout;\n    \n    clearTimeout(timeout);\n    \n    timeout = setTimeout(later, wait);\n    \n    if (callNow) func.apply(context, args);\n  };\n};"
            }
        }
        
        # Выбор кода на основе языка и категории
        if language in code_snippets and category in code_snippets[language]:
            code_snippet = code_snippets[language][category]
        else:
            # Резервный вариант, если нет подходящего примера
            code_snippet = f"// Example code for {language} in category {category}"
        
        # Создание объяснения для примера кода
        explanations = {
            "algorithm": f"This is an implementation of a popular algorithm in {language}. It demonstrates efficient problem solving.",
            "data-structure": f"A custom data structure implementation in {language} that shows how to organize and manage data efficiently.",
            "utility": f"A utility function in {language} that can be used across different projects to simplify common tasks.",
            "pattern": f"An implementation of a design pattern in {language} that shows best practices for code organization."
        }
        
        explanation = explanations.get(category, f"Example code for {language}")
        
        # В демо-версии возвращаем виртуальный пример, не сохраняя в БД
        example_data = {
            "id": random.randint(1000, 9999),  # Для демо используем случайный ID
            "language": language,
            "code_snippet": code_snippet,
            "explanation": explanation,
            "category": category
        }
        
        logger.info(f"Created new code example: {language} - {category}")
        
        # Создаем простой объект с атрибутом id для совместимости
        class SimpleObject:
            def __init__(self, id):
                self.id = id
                
        return SimpleObject(example_data["id"])
        
    except Exception as e:
        logger.error(f"Error creating code example: {str(e)}")
        return None

def process_feedback(feedback):
    """
    Process new feedback for continuous learning
    
    Args:
        feedback (Feedback): Feedback object
    """
    # Increment feedback count for this language
    feedback_counts[feedback.language] += 1
    
    # Check if we've reached the threshold to update the model
    if feedback_counts[feedback.language] >= Config.FEEDBACK_THRESHOLD:
        logger.info(f"Feedback threshold reached for {feedback.language}, triggering model update")
        
        # Get recent feedback for this language
        recent_feedback = Feedback.query.filter_by(
            language=feedback.language
        ).order_by(
            Feedback.created_at.desc()
        ).limit(100).all()
        
        # Prepare feedback data for model update
        feedback_data = []
        for fb in recent_feedback:
            # Only use feedback with corrected output
            if fb.corrected_output:
                feedback_data.append({
                    'input': fb.code_input,
                    'expected': fb.corrected_output or fb.model_output,
                    'feedback_type': fb.feedback_type
                })
        
        # Update model if we have valid feedback data
        if feedback_data:
            try:
                # Update model weights (simulated)
                update_result = update_model_weights(feedback_data)
                
                # Record model version update
                record_model_update(feedback.language, update_result, len(feedback_data))
                
                # Reset counter
                feedback_counts[feedback.language] = 0
                
            except Exception as e:
                logger.error(f"Error updating model for {feedback.language}: {str(e)}")
        else:
            logger.info(f"No valid feedback data for {feedback.language}, skipping update")

def record_completion_feedback(user_id, code_input, model_output, corrected_output, language, rating=None):
    """
    Record feedback for code completion
    
    Args:
        user_id (int): User ID
        code_input (str): Original code input
        model_output (str): Generated completion by model
        corrected_output (str): User corrected completion (optional)
        language (str): Programming language
        rating (int): User rating 1-5 (optional)
        
    Returns:
        Feedback: Created feedback object
    """
    try:
        feedback = Feedback(
            user_id=user_id,
            code_input=code_input,
            model_output=model_output,
            corrected_output=corrected_output,
            language=language,
            feedback_type='completion',
            rating=rating
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Process feedback for learning
        process_feedback(feedback)
        
        return feedback
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording completion feedback: {str(e)}")
        raise

def record_model_update(language, update_result, feedback_count):
    """
    Record a model update in the database
    
    Args:
        language (str): Programming language
        update_result (dict): Result from model update
        feedback_count (int): Number of feedback items used
    """
    try:
        # Create parameters JSON
        parameters = {
            "language": language,
            "feedback_count": feedback_count,
            "learning_rate": Config.LEARNING_RATE
        }
        
        # Create metrics JSON
        metrics = {
            "status": update_result.get("status", "unknown"),
            "message": update_result.get("message", "")
        }
        
        # Create new model version record
        model_version = ModelVersion(
            version=update_result.get("new_version", "0.1.0"),
            description=f"Updated model for {language} with {feedback_count} feedback items",
            parameters=json.dumps(parameters),
            performance_metrics=json.dumps(metrics)
        )
        
        db.session.add(model_version)
        db.session.commit()
        
        logger.info(f"Recorded model update: version {model_version.version}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording model update: {str(e)}")
