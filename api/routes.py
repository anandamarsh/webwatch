from flask import Blueprint, jsonify, request
from models.blocklist import get_blocklist, add_to_blocklist, remove_from_blocklist

# Create blueprint with url_prefix
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Main route
@api_bp.route('/')
def index():
    return {"status": "WebWatch API is running"}

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
