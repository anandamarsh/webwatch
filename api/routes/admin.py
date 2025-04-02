from flask import Blueprint, jsonify
from api.database import get_db_connection
from api import logger

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/clear', methods=['POST'])
def clear_database():
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear tables
        cursor.execute("DELETE FROM visits")
        cursor.execute("DELETE FROM content_store")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='visits'")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success", 
            "message": "Database cleared successfully"
        })
    
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/reset', methods=['POST'])
def reset_database():
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Drop tables
        cursor.execute("DROP TABLE IF EXISTS visits")
        cursor.execute("DROP TABLE IF EXISTS content_store")
        
        conn.commit()
        conn.close()
        
        # Reinitialize database
        from api.database import init_db
        init_db()
        
        return jsonify({
            "status": "success", 
            "message": "Database reset successfully"
        })
    
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return jsonify({"error": str(e)}), 500 