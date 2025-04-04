from flask import Blueprint, jsonify, request
from models.blocklist import get_blocklist, add_to_blocklist, remove_from_blocklist, clear_blocklist
from models.visits import get_visits, get_visits_for_report, add_visit, clear_visits, get_visit_by_url
from openai_utils import get_rating_and_report_from_file
import os
import re
import urllib.parse

# Create blueprint with url_prefix
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Ensure the 'webpages' directory exists
os.makedirs('webpages', exist_ok=True)

def save_html_content_to_file(url, content):
    # Sanitize the URL to create a valid filename
    sanitized_url = re.sub(r'[^a-zA-Z0-9]', '_', url[:100])
    filename = f"webpages/{sanitized_url}.html"
    
    # Decode the content if necessary
    decoded_content = urllib.parse.unquote(content)
    
    # Save the content to a file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(decoded_content)
    
    return filename

# Main route
@api_bp.route('/')
def index():
    return {"status": "WebWatch API is running"}

# Reset route
@api_bp.route('/reset', methods=['GET'])
def reset():
    try:
        # Clear the blocklist
        clear_blocklist()
        
        # Clear the visits
        clear_visits()
        
        return jsonify({"success": True, "message": "Database and blocklist reset successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to reset: {str(e)}"}), 500

# Blocklist routes
@api_bp.route('/blocklist', methods=['GET'])
def get_blocklist_route():
    try:
        blocklist = get_blocklist()
        return jsonify(blocklist)
    except Exception as e:
        return jsonify({"error": f"Failed to read blocklist file: {str(e)}"}), 500

@api_bp.route('/blocklist', methods=['POST'])
def add_blocklist_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        entry = add_to_blocklist(
            url=data['url'],
            reason=data.get('reason')
        )
        
        return jsonify({"success": True, "message": "Entry added to blocklist", "entry": entry}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to update blocklist file: {str(e)}"}), 500

@api_bp.route('/blocklist/<int:index>', methods=['DELETE'])
def delete_blocklist_route(index):
    try:
        removed_entry = remove_from_blocklist(index)
        return jsonify({"success": True, "message": "Entry removed from blocklist", "removed": removed_entry}), 200
    except IndexError:
        return jsonify({"error": "Invalid index"}), 400
    except FileNotFoundError:
        return jsonify({"error": "Blocklist file does not exist"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete blocklist entry: {str(e)}"}), 500

# Visits routes
@api_bp.route('/visits', methods=['GET'])
def get_visits_route():
    try:
        visits = get_visits()
        return jsonify(visits)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve visits: {str(e)}"}), 500

@api_bp.route('/visits', methods=['POST'])
def add_visit_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['url', 'content', 'title', 'timestamp']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        url = data['url']
        content = data['content']
        title = data['title']
        timestamp = data['timestamp']
        
        existing_visit = get_visit_by_url(url)
        if existing_visit:
            return jsonify({"success": True, "message": "Visit already exists", "visit": existing_visit}), 200
        
        # Save the HTML content to a file
        file_path = save_html_content_to_file(url, content)
        
        # Call the OpenAI Assistant with the file
        ai_result = get_rating_and_report_from_file(file_path)
        if ai_result:
            rating = ai_result.get('rating', -1)
            report = ai_result.get('report', 'No report provided')
            
            visit = add_visit(url, report, title, timestamp, rating)
            return jsonify({"success": True, "message": "Visit added", "visit": visit}), 201
        else:
            return jsonify({"error": "Failed to get AI results"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to add visit: {str(e)}"}), 500

# Report route
@api_bp.route('/report', methods=['GET'])
def report_route():
    try:
        blocklist = get_blocklist()
        visits = get_visits_for_report()
        report = {
            "blocklist": blocklist,
            "visits": visits
        }
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500
