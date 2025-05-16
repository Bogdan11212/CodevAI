"""
API for managing CodevAI's continuous learning system through the web interface
"""

import logging
import json
from flask import request, jsonify, current_app
from api import api_bp
from web_scraper import enqueue_url_for_learning, process_url_now, get_website_text_content
from brain.continuous_learning import count_knowledge_items, knowledge_base

logger = logging.getLogger(__name__)

@api_bp.route('/learning/enqueue', methods=['POST'])
def api_enqueue_url():
    """
    Add URL to the queue for processing by continuous learning system
    
    Expected JSON request:
    {
        "url": "https://example.com/python-tutorial"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Add URL to the queue for processing
    success = enqueue_url_for_learning(url)
    
    if success:
        return jsonify({"success": True, "message": "URL successfully added to queue"}), 200
    else:
        return jsonify({"success": False, "error": "Failed to add URL to queue"}), 400

@api_bp.route('/learning/process', methods=['POST'])
def api_process_url():
    """
    Immediately process URL for knowledge extraction
    
    Expected JSON request:
    {
        "url": "https://example.com/python-tutorial"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Process URL immediately
    result = process_url_now(url)
    
    return jsonify(result), 200 if result.get("success", False) else 400

@api_bp.route('/learning/content', methods=['POST'])
def api_get_url_content():
    """
    Get webpage content
    
    Expected JSON request:
    {
        "url": "https://example.com/python-tutorial"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Get webpage content
    content = get_website_text_content(url)
    
    return jsonify({"content": content}), 200

@api_bp.route('/learning/status', methods=['GET'])
def api_learning_status():
    """
    Get continuous learning system status
    """
    try:
        # Get knowledge base information
        item_count = count_knowledge_items()
        last_updated = knowledge_base.get("last_updated", "Never")
        
        # Form status by categories
        categories_status = {}
        for category in knowledge_base:
            if category != "last_updated":
                categories_status[category] = len(knowledge_base[category])
        
        return jsonify({
            "status": "active",
            "total_items": item_count,
            "last_updated": last_updated,
            "categories": categories_status
        }), 200
    except Exception as e:
        logger.error(f"Error getting learning system status: {str(e)}")
        return jsonify({"error": "Failed to get learning system status"}), 500