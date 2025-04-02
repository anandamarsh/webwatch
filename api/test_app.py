import unittest
import json
import os
import time
import tempfile
from unittest.mock import patch, MagicMock
import sqlite3
import nltk
from datetime import datetime, timedelta

# Download all required NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Use a file-based test database instead of in-memory
TEST_DB_PATH = "test_webwatch.db"

class WebWatchAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Download NLTK resources if needed
        nltk.download('punkt')
        nltk.download('stopwords')
    
    def setUp(self):
        # Remove test database if it exists
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)
        
        # Patch the Config.DB_PATH
        self.db_path_patcher = patch('api.config.Config.DB_PATH', TEST_DB_PATH)
        self.db_path_mock = self.db_path_patcher.start()
        
        # Import after patching
        from api import create_app
        from api.database import init_db
        
        # Initialize the database
        init_db()
        
        # Configure app for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Add some test data
        self.populate_test_data()
    
    def tearDown(self):
        # Stop the patcher
        self.db_path_patcher.stop()
        
        # Remove test database
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)
    
    def populate_test_data(self):
        """Add sample data to the database for testing"""
        # Import here to ensure patching is in effect
        from api.database import store_visit
        from api.utils import extract_text
        
        # Sample content
        content = "<html><body><h1>Test Page</h1><p>This is a test page content.</p></body></html>"
        
        # Insert visits
        for i in range(5):
            store_visit(
                url=f"https://example.com/page{i}",
                title=f"Test Page {i}",
                content=content,
                text_extract=extract_text(content),
                links=json.dumps([{"text": "Link 1", "href": "https://example.com/link1"}])
            )
        
        # Add a visit with sessions for testing report
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Add a session for the first visit
        now = datetime.now()
        start_time = (now - timedelta(hours=1)).isoformat()
        end_time = now.isoformat()
        
        cursor.execute(
            "INSERT INTO sessions (url, start_time, end_time, duration) VALUES (?, ?, ?, ?)",
            ("https://example.com/page0", start_time, end_time, 3600)
        )
        
        # Update the total_time_spent for the visit
        cursor.execute(
            "UPDATE visits SET total_time_spent = 3600 WHERE url = ?",
            ("https://example.com/page0",)
        )
        
        conn.commit()
        conn.close()
    
    def test_database_initialization(self):
        """Test that database tables are created properly"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        
        # Check visits table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visits'")
        self.assertIsNotNone(cursor.fetchone(), "Visits table should exist")
        
        # Check content_store table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='content_store'")
        self.assertIsNotNone(cursor.fetchone(), "Content store table should exist")
        
        # Check sessions table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        self.assertIsNotNone(cursor.fetchone(), "Sessions table should exist")
        
        conn.close()
    
    def test_register_visit(self):
        """Test the /visits endpoint for recording web activity"""
        test_data = {
            "url": "https://example.com/test",
            "title": "Test Activity",
            "content": "<html><body><h1>New Test</h1><p>This is new test content.</p></body></html>"
        }
        
        response = self.client.post(
            '/visits',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['url'], test_data['url'])
        
        # Verify data was stored
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visits WHERE url = ?", (test_data['url'],))
        visit = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(visit, "Visit should be stored in database")
    
    def test_missing_fields_visit(self):
        """Test that /visits rejects requests with missing fields"""
        test_data = {
            # Missing url
            "title": "Test Activity",
            "content": "<html><body><h1>New Test</h1><p>This is new test content.</p></body></html>"
        }
        
        response = self.client.post(
            '/visits',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_visits(self):
        """Test the /visits endpoint for retrieving visits"""
        response = self.client.get('/visits?days=30&limit=10')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should have our test visits
        self.assertGreaterEqual(len(data), 5)
    
    def test_get_report(self):
        """Test the /report endpoint for generating reports"""
        response = self.client.get('/report?days=30&limit=10')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check structure
        self.assertIn('period', data)
        self.assertIn('total_visits', data)
        self.assertIn('domain_statistics', data)
        self.assertIn('visits', data)
        
        # Should have our test visits
        self.assertGreaterEqual(len(data['visits']), 5)
        
        # Should have domain statistics
        self.assertGreaterEqual(len(data['domain_statistics']), 1)
        
        # First visit should have time spent
        first_visit = next((v for v in data['visits'] if v['url'] == 'https://example.com/page0'), None)
        self.assertIsNotNone(first_visit)
        self.assertEqual(first_visit['time_spent_formatted'], "1h 0m 0s")
    
    def test_get_visit_details(self):
        """Test the /visit/<url> endpoint for getting visit details"""
        url = "https://example.com/page0"
        response = self.client.get(f'/visit/{url}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check structure
        self.assertEqual(data['url'], url)
        self.assertEqual(data['title'], "Test Page 0")
        self.assertIn('timestamp', data)
        self.assertIn('text_extract', data)
        self.assertIn('links', data)
        
        # Should have links
        self.assertEqual(len(data['links']), 1)
        self.assertEqual(data['links'][0]['href'], "https://example.com/link1")
    
    def test_status_endpoint(self):
        """Test the /status endpoint"""
        response = self.client.get('/status')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check structure
        self.assertIn('status', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        
        # Status should be ok
        self.assertEqual(data['status'], 'ok')

if __name__ == '__main__':
    unittest.main() 