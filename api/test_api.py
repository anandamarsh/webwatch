import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:1978/api"

# Track test results
test_results = []

def print_separator():
    """Print a separator line for better readability"""
    print("\n" + "="*50 + "\n")

def log_test_result(test_name, success, message=""):
    """Log the result of a test"""
    test_results.append({
        "test_name": test_name,
        "success": success,
        "message": message
    })

def test_get_blocklist():
    """Test the GET /api/blocklist endpoint"""
    test_name = "GET /api/blocklist"
    print(f"Testing {test_name}...")
    
    try:
        response = requests.get(f"{BASE_URL}/blocklist")
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        log_test_result(test_name, True)
    except Exception as e:
        log_test_result(test_name, False, str(e))

def test_add_to_blocklist(url, reason=None):
    """Test the POST /api/blocklist endpoint"""
    test_name = f"POST /api/blocklist with URL: {url}"
    print(f"Testing {test_name}...")
    
    data = {"url": url}
    if reason:
        data["reason"] = reason
    
    try:
        response = requests.post(f"{BASE_URL}/blocklist", json=data)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        log_test_result(test_name, True)
    except Exception as e:
        log_test_result(test_name, False, str(e))

def test_delete_from_blocklist(index):
    """Test the DELETE /api/blocklist/<index> endpoint"""
    test_name = f"DELETE /api/blocklist/{index}"
    print(f"Testing {test_name}...")
    
    try:
        response = requests.delete(f"{BASE_URL}/blocklist/{index}")
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        log_test_result(test_name, True)
    except Exception as e:
        log_test_result(test_name, False, str(e))

def test_get_visits():
    """Test the GET /api/visits endpoint"""
    test_name = "GET /api/visits"
    print(f"Testing {test_name}...")
    
    try:
        response = requests.get(f"{BASE_URL}/visits")
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        log_test_result(test_name, True)
    except Exception as e:
        log_test_result(test_name, False, str(e))

def test_add_visit(url, report, title, timestamp):
    """Test the POST /api/visits endpoint"""
    test_name = f"POST /api/visits with URL: {url}"
    print(f"Testing {test_name}...")
    
    data = {
        "url": url,
        "content": "<html>Example Content</html>",  # Required but ignored
        "report": report,
        "title": title,
        "timestamp": timestamp
    }
    
    try:
        response = requests.post(f"{BASE_URL}/visits", json=data)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
        # Check if the response contains the expected fields
        visit_data = response.json().get('visit', {})
        assert visit_data.get('url') == url
        assert visit_data.get('report') == report
        assert visit_data.get('rating') == -1  # Ensure rating is initialized to -1
        
        log_test_result(test_name, True)
    except Exception as e:
        log_test_result(test_name, False, str(e))

def test_add_existing_visit(url, report, title, timestamp):
    """Test adding an existing visit returns the existing entry"""
    test_name = f"POST /api/visits with existing URL: {url}"
    print(f"Testing {test_name}...")
    
    data = {
        "url": url,
        "content": "<html>Example Content</html>",  # Required but ignored
        "report": report,
        "title": title,
        "timestamp": timestamp
    }
    
    try:
        response = requests.post(f"{BASE_URL}/visits", json=data)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
        # Access the 'visit' key in the response
        response_data = response.json()
        visit_data = response_data.get('visit', {})
        
        # Check if the response contains the expected fields for the existing entry
        assert visit_data['url'] == url, "URL mismatch"
        
        log_test_result(test_name, True)
    except Exception as e:
        # Print the response JSON for debugging
        try:
            print("Response JSON:", json.dumps(response.json(), indent=2))
        except Exception as json_error:
            print("Failed to parse JSON response:", str(json_error))
        
        log_test_result(test_name, False, str(e))

def test_get_report():
    """Test the GET /api/report endpoint"""
    test_name = "GET /api/report"
    print(f"Testing {test_name}...")
    
    try:
        response = requests.get(f"{BASE_URL}/report")
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        log_test_result(test_name, True)
    except Exception as e:
        log_test_result(test_name, False, str(e))

def run_all_tests():
    """Run all tests in sequence"""
    print_separator()
    print("STARTING API TESTS")
    print_separator()
    
    # Test 1: Get initial blocklist
    test_get_blocklist()
    print_separator()
    
    # Test 2: Add an entry to the blocklist
    test_add_to_blocklist("example.com", "Test entry")
    print_separator()
    
    # Test 3: Add another entry to the blocklist
    test_add_to_blocklist("test-site.org", "Another test entry")
    print_separator()
    
    # Test 4: Try to add a duplicate entry
    test_add_to_blocklist("example.com", "Updated reason")
    print_separator()
    
    # Test 5: Get updated blocklist
    test_get_blocklist()
    print_separator()
    
    # Test 6: Delete an entry (if there are any)
    updated_blocklist = test_get_blocklist()
    if updated_blocklist:
        test_delete_from_blocklist(0)
        print_separator()
        
        # Test 7: Get final blocklist
        test_get_blocklist()
        print_separator()
    
    # Test 8: Get initial visits
    test_get_visits()
    print_separator()
    
    # Test 9: Add a visit
    test_add_visit("https://example.com", "Example report", "Example Title", time.strftime("%Y-%m-%d %H:%M:%S"))
    print_separator()
    
    # Test 10: Add an existing visit
    test_add_existing_visit("https://example.com", "New report", "New Title", time.strftime("%Y-%m-%d %H:%M:%S"))
    print_separator()
    
    # Test 11: Get updated visits
    test_get_visits()
    print_separator()
    
    # Test 12: Get report
    test_get_report()
    print_separator()
    
    print("ALL TESTS COMPLETED")
    print_separator()
    print("TEST SUMMARY")
    print_separator()
    for result in test_results:
        status = "PASSED" if result["success"] else "FAILED"
        print(f"{result['test_name']}: {status}")
        if not result["success"]:
            print(f"  Error: {result['message']}")
    print_separator()

if __name__ == "__main__":
    # Make sure the API server is running before executing these tests
    print("Make sure the API server is running at http://localhost:1978")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API server.")
        print("Make sure the server is running at http://localhost:1978") 