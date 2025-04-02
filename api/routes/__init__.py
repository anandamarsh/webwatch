import logging
import sys

logger = logging.getLogger(__name__)

# Force output to console
print("DIRECT PRINT: Initializing routes/__init__.py", file=sys.stdout)
sys.stdout.flush()

try:
    from .visit import visit_bp  # Import the renamed blueprint
except ImportError:
    # Try alternative names that might be used
    try:
        from .visit import bp as visit_bp
    except ImportError:
        print("Warning: Could not import visit blueprint")
        visit_bp = None

try:
    from .admin import admin_bp
except ImportError:
    try:
        from .admin import bp as admin_bp
    except ImportError:
        print("Warning: Could not import admin blueprint")
        admin_bp = None

try:
    from .blocklist import blocklist_bp
except ImportError:
    try:
        from .blocklist import bp as blocklist_bp
    except ImportError:
        print("Warning: Could not import blocklist blueprint")
        blocklist_bp = None

try:
    from .report import report_bp
except ImportError:
    try:
        from .report import bp as report_bp
    except ImportError:
        print("Warning: Could not import report blueprint")
        report_bp = None

try:
    from .search import search_bp
except ImportError:
    try:
        from .search import bp as search_bp
    except ImportError:
        print("Warning: Could not import search blueprint")
        search_bp = None

# Import the status blueprint
try:
    from .status import status_bp
except ImportError:
    try:
        from .status import bp as status_bp
    except ImportError:
        print("Warning: Could not import status blueprint")
        status_bp = None

def init_app(app):
    # Register blueprints that were successfully imported
    if 'visit_bp' in globals() and visit_bp is not None:
        app.register_blueprint(visit_bp)
        logger.info("Registered visit_bp")
    if 'admin_bp' in globals() and admin_bp is not None:
        app.register_blueprint(admin_bp)
        logger.info("Registered admin_bp")
    if 'blocklist_bp' in globals() and blocklist_bp is not None:
        app.register_blueprint(blocklist_bp)
        logger.info("Registered blocklist_bp")
    if 'report_bp' in globals() and report_bp is not None:
        app.register_blueprint(report_bp)
        logger.info("Registered report_bp")
    if 'search_bp' in globals() and search_bp is not None:
        app.register_blueprint(search_bp)
        logger.info("Registered search_bp")
    if 'status_bp' in globals() and status_bp is not None:
        app.register_blueprint(status_bp)
        logger.info("Registered status_bp")
    else:
        logger.warning("status_bp not found in globals") 