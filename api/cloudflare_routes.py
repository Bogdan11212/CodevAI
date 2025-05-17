"""
API routes for Cloudflare AI features
"""

from flask import Blueprint, request, jsonify
from api.cloudflare_gateway import cloudflare
import logging
import json

logger = logging.getLogger(__name__)

# Create Blueprint
cloudflare_bp = Blueprint('cloudflare_api', __name__, url_prefix='/api/cloudflare')

@cloudflare_bp.route('/text-generation', methods=['POST'])
def text_generation():
    """API endpoint for text generation with Cloudflare AI"""
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({
            'success': False,
            'error': 'Prompt is required'
        }), 400
    
    prompt = data.get('prompt')
    model = data.get('model', 'llama3-8b')
    
    # Call Cloudflare AI
    result = cloudflare.chat_completion(prompt, model=model)
    
    if result.get('success'):
        return jsonify({
            'success': True,
            'text': result.get('text', ''),
            'model': model
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to generate text')
        }), 500

@cloudflare_bp.route('/code-analysis', methods=['POST'])
def code_analysis():
    """API endpoint for code analysis with Cloudflare AI"""
    data = request.json
    
    if not data or 'code' not in data:
        return jsonify({
            'success': False,
            'error': 'Code is required'
        }), 400
    
    code = data.get('code')
    language = data.get('language')
    task = data.get('task', 'review')
    
    # Call Cloudflare AI
    result = cloudflare.analyze_code(code, language, task)
    
    if result.get('success'):
        return jsonify({
            'success': True,
            'text': result.get('text', '')
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to analyze code')
        }), 500

@cloudflare_bp.route('/image-generation', methods=['POST'])
def image_generation():
    """API endpoint for image generation with Cloudflare AI"""
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({
            'success': False,
            'error': 'Prompt is required'
        }), 400
    
    prompt = data.get('prompt')
    
    # Call Cloudflare AI
    result = cloudflare.generate_image(prompt)
    
    if result.get('success'):
        return jsonify({
            'success': True,
            'image_data': result.get('image_data', '')
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to generate image')
        }), 500

@cloudflare_bp.route('/moderate-content', methods=['POST'])
def moderate_content():
    """API endpoint for content moderation with Cloudflare AI"""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'Text is required'
        }), 400
    
    text = data.get('text')
    
    # Call Cloudflare AI
    result = cloudflare.moderate_content(text)
    
    if result.get('success'):
        try:
            # Extract moderation categories and scores
            categories = result.get('result', {}).get('result', {})
            
            return jsonify({
                'success': True,
                'categories': categories
            })
        except Exception as e:
            logger.error(f"Error processing moderation result: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error processing moderation result'
            }), 500
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to moderate content')
        }), 500

@cloudflare_bp.route('/extract-knowledge', methods=['POST'])
def extract_knowledge():
    """API endpoint for knowledge extraction with Cloudflare AI"""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'Text is required'
        }), 400
    
    text = data.get('text')
    topic = data.get('topic')
    
    # Call Cloudflare AI
    result = cloudflare.learn_from_text(text, topic)
    
    if result.get('success'):
        return jsonify({
            'success': True,
            'knowledge': result.get('knowledge', {})
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to extract knowledge')
        }), 500

@cloudflare_bp.route('/status', methods=['GET'])
def status():
    """Check Cloudflare API status"""
    has_credentials = cloudflare.has_credentials()
    
    return jsonify({
        'success': True,
        'status': 'connected' if has_credentials else 'disconnected',
        'has_credentials': has_credentials
    })