import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    DEBUG = True
    
    # Database settings - используем локальную SQLite базу данных
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/codevai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    API_RATE_LIMIT = 100  # requests per hour
    
    # Model settings
    SUPPORTED_LANGUAGES = ['python', 'javascript', 'java', 'cpp', 'go']
    DEFAULT_MODEL = 'distilbert-base-uncased'  # Lightweight model
    MODEL_CACHE_DIR = 'model_cache'
    
    # Learning settings
    FEEDBACK_THRESHOLD = 10  # Number of feedback items before updating model weights
    LEARNING_RATE = 0.0001
    
    # Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
