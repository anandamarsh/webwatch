from flask import Flask
from flask_cors import CORS

def create_app():
    # Create and configure the app
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Register blueprints
    from routes import api_bp
    app.register_blueprint(api_bp)
    
    return app
