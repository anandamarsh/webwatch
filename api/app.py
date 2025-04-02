from api import create_app
from api.config import Config
from api.database import init_db

app = create_app()
print("URL Map:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")

if __name__ == '__main__':
    # Initialize the database
    init_db()
    
    # Create and run the app
    app.run(host=Config.HOST, port=Config.PORT, debug=True)