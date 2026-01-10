import requests
import uuid

API_URL = "http://localhost:8000/chat"
SESSION_ID = str(uuid.uuid4())

def debug_query(q):
    print(f"\nSending query: '{q}'")
    try:
        response = requests.post(
            API_URL, 
            json={"query": q, "session_id": SESSION_ID},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print("Raw JSON response:")
        print(response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_query("Hi")
    debug_query("1")
