import logging
from flask import render_template, jsonify
from app import app
from utils.model_utils import get_language_model_version
from datetime import datetime

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Demo page for testing the API"""
    model_info = get_language_model_version()
    return render_template('demo.html', model_info=model_info)

@app.route('/documentation')
def documentation():
    """API documentation page"""
    return render_template('documentation.html', model_info=get_language_model_version())

@app.route('/code-generator')
def code_generator():
    """Code generation page with continuous learning"""
    return render_template('code_generator.html')

@app.route('/ai-thinking')
def ai_thinking_page():
    """AI Thinking page that shows the model's thought process"""
    return render_template('ai_thinking.html')

@app.route('/api/learning-status')
def learning_status():
    """API endpoint to get current learning status"""
    # В реальном приложении здесь запрашивались бы данные из БД
    # Для демо возвращаем фиктивные данные
    try:
        from utils.learning_utils import model_improvement_stats
        return jsonify(model_improvement_stats)
    except Exception as e:
        # В случае ошибки возвращаем фиктивные данные
        return jsonify({
            "iterations": 5,
            "last_updated": datetime.utcnow().isoformat(),
            "improvements": [],
            "total_samples_processed": 25
        })

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500
