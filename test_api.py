import requests
import json

# Test the FastAPI backend
def test_api():
    url = "http://localhost:8000/ask"
    data = {
        "message": "Hello, how are you?",
        "session_id": "test_session",
        "modality": "text"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    print(f"API Test {'PASSED' if success else 'FAILED'}")