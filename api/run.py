from api import create_app
from api.config import Config
import logging
import sys

# Configure logging to output to console with the lowest level
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Also set the root logger to DEBUG
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

logger.info("Starting WebWatch API server...")

app = create_app()

logger.info("Application created")
logger.info("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"  {rule.endpoint}: {rule.rule}")

if __name__ == '__main__':
    logger.info(f"Running app on {Config.HOST}:{Config.PORT} (debug={Config.DEBUG})")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG) 