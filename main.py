import threading
import time
import logging
from app import app
from utils.learning_utils import continuous_learning_task

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Запуск задачи непрерывного обучения в отдельном потоке
def start_continuous_learning():
    logger.info("Starting continuous learning thread...")
    learning_thread = threading.Thread(target=continuous_learning_task, daemon=True)
    learning_thread.start()
    logger.info("Continuous learning thread started")

if __name__ == "__main__":
    # Инициализация системы непрерывного обучения
    start_continuous_learning()
    
    # Запуск веб-сервера
    app.run(host="0.0.0.0", port=5000, debug=True)
