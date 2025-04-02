from flask import Blueprint, jsonify
import logging
import sys

# Create a direct console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Get the logger and add the console handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Force output to console
print("DIRECT PRINT: Importing status blueprint", file=sys.stdout)
sys.stdout.flush()

logger.debug("Importing status blueprint")

# Define the blueprint with the name 'bp' to match the import in __init__.py
bp = Blueprint('status', __name__)

@bp.route('/status', methods=['GET'])
def status():
    """Return API status information"""
    # Force output to console
    print("DIRECT PRINT: Status endpoint called", file=sys.stdout)
    sys.stdout.flush()
    
    logger.debug("Status endpoint called")
    return jsonify({
        "status": "ok",
        "version": "1.0",
        "endpoints": {
            "track": "/track",
            "sessions": "/sessions/start, /sessions/end",
            "blocklist": "/blocklist",
            "report": "/report"
        }
    })

# Force output to console
print("DIRECT PRINT: Status blueprint imported successfully", file=sys.stdout)
sys.stdout.flush()

logger.debug("Status blueprint imported successfully")