from flask import Blueprint, request, jsonify
import json
import os
import datetime
from api.database import get_db_connection
from api import logger

blocklist_bp = Blueprint('blocklist', __name__)

# Path to store the blocklist
BLOCKLIST_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'blocklist.json')

# Ensure data directory exists
os.makedirs(os.path.dirname(BLOCKLIST_FILE), exist_ok=True)

def get_blocklist():
    """Get the current blocklist - read from file every time"""
    try:
        if os.path.exists(BLOCKLIST_FILE):
            with open(BLOCKLIST_FILE, 'r') as f:
                return json.load(f)
        else:
            # Initialize with empty list
            with open(BLOCKLIST_FILE, 'w') as f:
                json.dump([], f)
            return []
    except Exception as e:
        logger.error(f"Error reading blocklist: {str(e)}")
        return []

def save_blocklist(blocklist):
    """Save the blocklist to file"""
    try:
        with open(BLOCKLIST_FILE, 'w') as f:
            json.dump(blocklist, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving blocklist: {str(e)}")
        return False

@blocklist_bp.route('/blocklist', methods=['GET'])
def get_blocked_urls():
    """Get the list of blocked URLs - reads from file every time"""
    try:
        # Always read from file to get the latest blocklist
        blocklist = get_blocklist()
        return jsonify(blocklist)
    except Exception as e:
        logger.error(f"Error getting blocklist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@blocklist_bp.route('/blocklist', methods=['POST'])
def add_blocked_url():
    """Add a URL to the blocklist"""
    try:
        data = request.json
        
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        reason = data.get('reason', 'Manually blocked')
        
        # Always read from file to get the latest blocklist
        blocklist = get_blocklist()
        
        # Check if URL is already blocked
        for item in blocklist:
            if item['url'] == url:
                # If it's already blocked, update the reason if provided
                if reason and reason != 'Manually blocked':
                    item['reason'] = reason
                    item['updated'] = datetime.datetime.now().isoformat()
                    if save_blocklist(blocklist):
                        return jsonify({"status": "success", "message": f"URL {url} updated successfully"}), 200
                    else:
                        return jsonify({"error": "Failed to save blocklist"}), 500
                return jsonify({"error": "URL is already blocked"}), 400
        
        # Add URL to blocklist
        blocklist.append({
            "url": url,
            "reason": reason,
            "added": datetime.datetime.now().isoformat()
        })
        
        # Save blocklist
        if save_blocklist(blocklist):
            return jsonify({"status": "success", "message": f"URL {url} blocked successfully"}), 201
        else:
            return jsonify({"error": "Failed to save blocklist"}), 500
    
    except Exception as e:
        logger.error(f"Error adding to blocklist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@blocklist_bp.route('/blocklist/<path:url>', methods=['DELETE'])
def remove_blocked_url(url):
    """Remove a URL from the blocklist"""
    try:
        # Always read from file to get the latest blocklist
        blocklist = get_blocklist()
        
        # Find and remove URL
        for i, item in enumerate(blocklist):
            if item['url'] == url:
                del blocklist[i]
                
                # Save blocklist
                if save_blocklist(blocklist):
                    return jsonify({"status": "success", "message": f"URL {url} unblocked successfully"})
                else:
                    return jsonify({"error": "Failed to save blocklist"}), 500
        
        return jsonify({"error": "URL not found in blocklist"}), 404
    
    except Exception as e:
        logger.error(f"Error removing from blocklist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@blocklist_bp.route('/blocklist/check', methods=['POST'])
def check_url():
    """Check if a URL is blocked"""
    try:
        data = request.json
        
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        
        # Always read from file to get the latest blocklist
        blocklist = get_blocklist()
        
        # Check if URL matches any blocked pattern
        for item in blocklist:
            blocked_url = item['url']
            
            # Exact match
            if url == blocked_url:
                return jsonify({"blocked": True, "reason": item['reason']})
            
            # Domain match (if blocked URL starts with domain:)
            if blocked_url.startswith('domain:'):
                domain = blocked_url[7:]  # Remove 'domain:' prefix
                if domain in url:
                    return jsonify({"blocked": True, "reason": item['reason']})
            
            # Pattern match (if blocked URL contains *)
            if '*' in blocked_url:
                import re
                pattern = blocked_url.replace('.', '\\.').replace('*', '.*')
                if re.match(pattern, url):
                    return jsonify({"blocked": True, "reason": item['reason']})
        
        return jsonify({"blocked": False})
    
    except Exception as e:
        logger.error(f"Error checking blocklist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@blocklist_bp.route('/blocklist/<path:url>', methods=['PUT'])
def update_blocked_url(url):
    """Update a URL in the blocklist"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        new_reason = data.get('reason')
        
        # Always read from file to get the latest blocklist
        blocklist = get_blocklist()
        
        # Find and update URL
        for item in blocklist:
            if item['url'] == url:
                if new_reason is not None:
                    item['reason'] = new_reason
                
                item['updated'] = datetime.datetime.now().isoformat()
                
                # Save blocklist
                if save_blocklist(blocklist):
                    return jsonify({"status": "success", "message": f"URL {url} updated successfully"})
                else:
                    return jsonify({"error": "Failed to save blocklist"}), 500
        
        return jsonify({"error": "URL not found in blocklist"}), 404
    
    except Exception as e:
        logger.error(f"Error updating blocklist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@blocklist_bp.route('/blocklist/bulk', methods=['POST'])
def bulk_add_blocked_urls():
    """Add multiple URLs to the blocklist at once"""
    try:
        data = request.json
        
        if not data or 'urls' not in data or not isinstance(data['urls'], list):
            return jsonify({"error": "List of URLs is required"}), 400
        
        urls = data['urls']
        default_reason = data.get('reason', 'Bulk import')
        
        # Always read from file to get the latest blocklist
        blocklist = get_blocklist()
        
        # Track results
        added = []
        skipped = []
        
        # Process each URL
        for url_item in urls:
            # Handle both string URLs and objects with url/reason
            if isinstance(url_item, str):
                url = url_item
                reason = default_reason
            else:
                url = url_item.get('url')
                reason = url_item.get('reason', default_reason)
            
            if not url:
                continue
            
            # Check if URL is already blocked
            already_blocked = False
            for item in blocklist:
                if item['url'] == url:
                    skipped.append(url)
                    already_blocked = True
                    break
            
            if not already_blocked:
                # Add URL to blocklist
                blocklist.append({
                    "url": url,
                    "reason": reason,
                    "added": datetime.datetime.now().isoformat()
                })
                added.append(url)
        
        # Save blocklist if any URLs were added
        if added:
            if save_blocklist(blocklist):
                return jsonify({
                    "status": "success", 
                    "added": added, 
                    "skipped": skipped,
                    "message": f"Added {len(added)} URLs to blocklist"
                }), 201
            else:
                return jsonify({"error": "Failed to save blocklist"}), 500
        else:
            return jsonify({
                "status": "success", 
                "added": [], 
                "skipped": skipped,
                "message": "No new URLs added to blocklist"
            }), 200
    
    except Exception as e:
        logger.error(f"Error bulk adding to blocklist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@blocklist_bp.route('/blocklist/export', methods=['GET'])
def export_blocklist():
    """Export the blocklist as a downloadable JSON file"""
    try:
        # Always read from file to get the latest blocklist
        blocklist = get_blocklist()
        
        # Create a response with the blocklist as JSON
        response = jsonify(blocklist)
        response.headers.set('Content-Disposition', 'attachment', filename='blocklist.json')
        return response
    
    except Exception as e:
        logger.error(f"Error exporting blocklist: {str(e)}")
        return jsonify({"error": str(e)}), 500 