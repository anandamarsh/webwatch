from flask import Blueprint, request, jsonify
import json
from api.database import store_visit, get_visits
from api.utils import extract_text, extract_links, is_localhost_url
from api import logger

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/visits', methods=['GET'])
def list_visits():
    """Return a list of all visits"""
    # Get query parameters
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    try:
        # Use our database function to get visits
        visits = get_visits(days, limit)
        
        # Return the visits as JSON
        return jsonify(visits)
    except Exception as e:
        logger.error(f"Error querying visits: {e}")
        return jsonify({"error": "Failed to retrieve visits: " + str(e)}), 500

@activity_bp.route('/visits', methods=['POST'])
def register_visit():
    """Register a new visit"""
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Extract required fields
    url = data.get('url')
    title = data.get('title', '')
    content = data.get('content')
    timestamp = data.get('timestamp')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    # Skip localhost URLs
    if is_localhost_url(url):
        logger.info(f"Ignoring localhost URL: {url}")
        return jsonify({"status": "skipped", "message": "Localhost URLs are ignored"}), 200
    
    try:
        # Process content if available
        text_extract = None
        links_json = None
        
        if content:
            # Extract text from content
            text_extract = extract_text(content)
            
            # Extract links from content
            links = extract_links(content, base_url=url)
            links_json = json.dumps(links)
        
        # Use our database function to store the visit
        result = store_visit(
            url=url,
            title=title,
            content=content,
            text_extract=text_extract,
            links=links_json
        )
        
        logger.info(f"Recorded visit for URL: {url}")
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error registering visit: {e}")
        return jsonify({"error": "Failed to register visit: " + str(e)}), 500 