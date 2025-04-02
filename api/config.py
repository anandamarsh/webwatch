import os

class Config:
    """Application configuration"""
    # Database settings
    DB_PATH = os.environ.get('DB_PATH', 'webwatch.db')
    PERSIST_DB = os.environ.get('PERSIST_DB', 'true').lower() == 'true'
    PERSIST_DB_PATH = os.environ.get('PERSIST_DB_PATH', 'webwatch_persist.db')
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 1978))
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true" 
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # API configuration
    API_PREFIX = os.environ.get('API_PREFIX', '') 