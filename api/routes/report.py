from flask import Blueprint, request, jsonify
import json
import datetime
from api.database import get_db_connection
from api import logger

report_bp = Blueprint('report', __name__)

@report_bp.route('/report', methods=['GET'])
def get_report():
    try:
        # Get query parameters
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 100))
        domain_filter = request.args.get('domain')
        
        # Calculate date range
        end_date = datetime.datetime.now().isoformat()
        start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT url, title, timestamp, content_hash, text_extract, links, total_time_spent
            FROM visits
            WHERE timestamp BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if domain_filter:
            query += " AND url LIKE ?"
            params.append(f"%{domain_filter}%")
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor.execute(query, params)
        visits = []
        
        for row in cursor.fetchall():
            visit_dict = dict(row)
            
            # Parse links JSON if it exists
            if visit_dict.get('links'):
                try:
                    visit_dict['links'] = json.loads(visit_dict['links'])
                except:
                    visit_dict['links'] = []
            else:
                visit_dict['links'] = []
            
            # Get sessions for this URL
            sessions_cursor = conn.cursor()
            sessions_cursor.execute("""
                SELECT id, start_time, end_time, duration
                FROM sessions
                WHERE url = ? AND start_time BETWEEN ? AND ?
                ORDER BY start_time DESC
            """, (visit_dict['url'], start_date, end_date))
            
            visit_dict['sessions'] = [dict(session) for session in sessions_cursor.fetchall()]
            
            # Format time spent in a human-readable format
            total_seconds = visit_dict.get('total_time_spent', 0)
            if total_seconds:
                minutes, seconds = divmod(total_seconds, 60)
                hours, minutes = divmod(minutes, 60)
                visit_dict['time_spent_formatted'] = f"{hours}h {minutes}m {seconds}s"
            else:
                visit_dict['time_spent_formatted'] = "0s"
                
            visits.append(visit_dict)
        
        # Get domain statistics with time spent
        domain_query = """
            SELECT 
                substr(url, instr(url, '://') + 3, 
                       case when instr(substr(url, instr(url, '://') + 3), '/') = 0 
                            then length(substr(url, instr(url, '://') + 3))
                            else instr(substr(url, instr(url, '://') + 3), '/') - 1
                       end) as domain,
                COUNT(*) as count,
                SUM(total_time_spent) as total_time_spent
            FROM visits
            WHERE timestamp BETWEEN ? AND ?
        """
        domain_params = [start_date, end_date]
        
        if domain_filter:
            domain_query += " AND url LIKE ?"
            domain_params.append(f"%{domain_filter}%")
        
        domain_query += " GROUP BY domain ORDER BY total_time_spent DESC LIMIT 10"
        
        cursor.execute(domain_query, domain_params)
        domains = []
        
        for row in cursor.fetchall():
            domain_dict = dict(row)
            
            # Format time spent
            total_seconds = domain_dict.get('total_time_spent', 0)
            if total_seconds:
                minutes, seconds = divmod(total_seconds, 60)
                hours, minutes = divmod(minutes, 60)
                domain_dict['time_spent_formatted'] = f"{hours}h {minutes}m {seconds}s"
            else:
                domain_dict['time_spent_formatted'] = "0s"
                
            domains.append(domain_dict)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM visits WHERE timestamp BETWEEN ? AND ?"
        count_params = [start_date, end_date]
        
        if domain_filter:
            count_query += " AND url LIKE ?"
            count_params.append(f"%{domain_filter}%")
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "period": {
                "start": start_date,
                "end": end_date,
                "days": days
            },
            "total_visits": total_count,
            "domain_statistics": domains,
            "visits": visits
        })
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({"error": str(e)}), 500

@report_bp.route('/visit/<path:url>', methods=['GET'])
def get_visit_details(url):
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get visit details
        cursor.execute("""
            SELECT v.url, v.title, v.timestamp, v.text_extract, v.content_hash, v.links,
                   cs.metadata
            FROM visits v
            JOIN content_store cs ON v.content_hash = cs.hash
            WHERE v.url = ?
        """, (url,))
        
        visit = cursor.fetchone()
        
        if not visit:
            return jsonify({"error": "Visit not found"}), 404
        
        # Convert to dict and parse metadata
        visit_dict = dict(visit)
        if visit_dict.get('metadata'):
            try:
                visit_dict['metadata'] = json.loads(visit_dict['metadata'])
            except:
                visit_dict['metadata'] = {}
        else:
            visit_dict['metadata'] = {}
        
        # Parse links JSON if it exists
        if visit_dict.get('links'):
            try:
                visit_dict['links'] = json.loads(visit_dict['links'])
            except:
                visit_dict['links'] = []
        else:
            visit_dict['links'] = []
        
        # Optionally include content
        if request.args.get('include_content') == 'true':
            content_cursor = conn.cursor()
            content_cursor.execute("SELECT content FROM content_store WHERE hash = ?", 
                                  (visit_dict['content_hash'],))
            content = content_cursor.fetchone()
            if content:
                visit_dict['content'] = content['content']
        
        conn.close()
        
        return jsonify(visit_dict)
    
    except Exception as e:
        logger.error(f"Error getting visit details: {str(e)}")
        return jsonify({"error": str(e)}), 500 