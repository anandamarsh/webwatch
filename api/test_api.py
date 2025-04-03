import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:1978/api"

def print_separator():
    """Print a separator line for better readability"""
    print("\n" + "="*50 + "\n")

def test_get_blocklist():
    """Test the GET /api/blocklist endpoint"""
    print("Testing GET /api/blocklist...")
    
    response = requests.get(f"{BASE_URL}/blocklist")
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_add_to_blocklist(url, reason=None):
    """Test the POST /api/blocklist endpoint"""
    print(f"Testing POST /api/blocklist with URL: {url}")
    
    data = {"url": url}
    if reason:
        data["reason"] = reason
    
    response = requests.post(
        f"{BASE_URL}/blocklist",
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_delete_from_blocklist(index):
    """Test the DELETE /api/blocklist/<index> endpoint"""
    print(f"Testing DELETE /api/blocklist/{index}")
    
    response = requests.delete(f"{BASE_URL}/blocklist/{index}")
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_get_visits():
    """Test the GET /api/visits endpoint"""
    print("Testing GET /api/visits...")
    
    response = requests.get(f"{BASE_URL}/visits")
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_add_visit(url, content, title, timestamp):
    """Test the POST /api/visits endpoint"""
    print(f"Testing POST /api/visits with URL: {url}")
    
    data = {
        "url": url,
        "content": content,
        "title": title,
        "timestamp": timestamp
    }
    
    response = requests.post(
        f"{BASE_URL}/visits",
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def run_all_tests():
    """Run all tests in sequence"""
    print_separator()
    print("STARTING API TESTS")
    print_separator()
    
    # Test 1: Get initial blocklist
    print("Test 1: Get initial blocklist")
    initial_blocklist = test_get_blocklist()
    print_separator()
    
    # Test 2: Add an entry to the blocklist
    print("Test 2: Add an entry to the blocklist")
    test_add_to_blocklist("example.com", "Test entry")
    print_separator()
    
    # Test 3: Add another entry to the blocklist
    print("Test 3: Add another entry to the blocklist")
    test_add_to_blocklist("test-site.org", "Another test entry")
    print_separator()
    
    # Test 4: Try to add a duplicate entry
    print("Test 4: Try to add a duplicate entry")
    test_add_to_blocklist("example.com", "Updated reason")
    print_separator()
    
    # Test 5: Get updated blocklist
    print("Test 5: Get updated blocklist")
    updated_blocklist = test_get_blocklist()
    print_separator()
    
    # Test 6: Delete an entry (if there are any)
    if updated_blocklist:
        print("Test 6: Delete the first entry")
        test_delete_from_blocklist(0)
        print_separator()
        
        # Test 7: Get final blocklist
        print("Test 7: Get final blocklist")
        test_get_blocklist()
        print_separator()
    
    # Test 8: Get initial visits
    print("Test 8: Get initial visits")
    initial_visits = test_get_visits()
    print_separator()
    
    # Test 9: Add a visit
    print("Test 9: Add a visit")
    test_add_visit("https://example.com", "Example content", "Example Title", time.strftime("%Y-%m-%d %H:%M:%S"))
    print_separator()
    
    # Test 10: Get updated visits
    print("Test 10: Get updated visits")
    test_get_visits()
    print_separator()
    
    print("ALL TESTS COMPLETED")

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