import logging
from flask import render_template
from app import app
from utils.model_utils import get_language_model_version

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

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500
