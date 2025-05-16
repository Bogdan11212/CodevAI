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

@app.route('/interactive-editor')
def interactive_editor():
    """Interactive code editor with integrated AI assistance"""
    return render_template('interactive_editor.html')

@app.route('/api/learning-status')
def learning_status():
    """API endpoint to get current learning status"""
    try:
        from brain.continuous_learning import get_learning_status
        return jsonify(get_learning_status())
    except Exception as e:
        logger.error(f"Error getting learning status: {str(e)}")
        return jsonify({
            "error": "Failed to get learning status",
            "is_learning": False,
            "knowledge_items": 0,
            "last_updated": datetime.utcnow().isoformat()
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
