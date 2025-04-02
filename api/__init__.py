from flask import Flask
from flask_cors import CORS
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(config_object=None):
    """Create and configure the Flask application"""
    # Force output to console
    print("DIRECT PRINT: Creating Flask application", file=sys.stdout)
    sys.stdout.flush()
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        from api.config import Config
        app.config.from_object(Config)
    
    # Initialize database
    from api.database import init_db
    init_db()
    
    # Register blueprints using the init_app function from routes
    from api.routes import init_app as init_routes
    init_routes(app)
    
    # Register blueprints
    from api.routes.visit import visit_bp
    from api.routes.blocklist import blocklist_bp
    
    # Register the blueprints with the app
    app.register_blueprint(visit_bp)
    app.register_blueprint(blocklist_bp)
    
    # Simple index route
    @app.route('/')
    def index():
        return {"status": "WebWatch API is running"}
    
    # Force output to console
    print("DIRECT PRINT: Flask application created and blueprints registered", file=sys.stdout)
    sys.stdout.flush()
    
    return app 