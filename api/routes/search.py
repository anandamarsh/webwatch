from flask import Blueprint, request, jsonify
import json
from api.database import get_db_connection
from api import logger

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_visits():
    try:
        # Get query parameters
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search in visits and content
        cursor.execute("""
            SELECT v.url, v.title, v.timestamp, v.text_extract, v.links
            FROM visits v
            JOIN content_store cs ON v.content_hash = cs.hash
            WHERE v.url LIKE ? OR v.title LIKE ? OR v.text_extract LIKE ? 
                  OR cs.content LIKE ? OR cs.metadata LIKE ?
            ORDER BY v.timestamp DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            result_dict = dict(row)
            
            # Parse links JSON if it exists
            if result_dict.get('links'):
                try:
                    result_dict['links'] = json.loads(result_dict['links'])
                except:
                    result_dict['links'] = []
            else:
                result_dict['links'] = []
                
            results.append(result_dict)
        
        conn.close()
        
        return jsonify({
            "query": query,
            "count": len(results),
            "results": results
        })
    
    except Exception as e:
        logger.error(f"Error searching visits: {str(e)}")
        return jsonify({"error": str(e)}), 500

@search_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total visits
        cursor.execute("SELECT COUNT(*) FROM visits")
        total_visits = cursor.fetchone()[0]
        
        # Get total unique domains
        cursor.execute("""
            SELECT COUNT(DISTINCT 
                substr(url, instr(url, '://') + 3, 
                       case when instr(substr(url, instr(url, '://') + 3), '/') = 0 
                            then length(substr(url, instr(url, '://') + 3))
                            else instr(substr(url, instr(url, '://') + 3), '/') - 1
                       end)
            ) FROM visits
        """)
        unique_domains = cursor.fetchone()[0]
        
        # Get visits by day for the last 30 days
        cursor.execute("""
            SELECT date(timestamp) as day, COUNT(*) as count
            FROM visits
            WHERE timestamp >= date('now', '-30 days')
            GROUP BY day
            ORDER BY day
        """)
        daily_visits = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "total_visits": total_visits,
            "unique_domains": unique_domains,
            "daily_visits": daily_visits
        })
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"error": str(e)}), 500 