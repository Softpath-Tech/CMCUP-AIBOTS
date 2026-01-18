
import requests
import json

def test_api_faq():
    print("Testing API RAG Query...")
    
    url = "http://127.0.0.1:8000/ask"
    
    # Test Question from the new list
    question = "What is the website about?"
    expected_keyword = "portal of the Telangana state agency"
    
    payload = {
        "query": question,
        "session_id": "test_verification_session"
    }
    
    try:
        print(f"Sending POST to {url} with query: '{question}'")
        resp = requests.post(url, json=payload, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            # The API returns different structures depending on version, but typically it returns the text directly or a dict.
            # Based on api/main.py: return create_api_response(final_answer...
            # create_api_response usually wraps it in specific JSON structure or just returns JSON.
            
            # Let's print raw first
            print(f"Raw Response: {data}")
            
            # Assuming 'message' or 'response' field, or just the body if it's returns dict
            ans = str(data)
            
            if expected_keyword.lower() in ans.lower() or "sports authority" in ans.lower():
                print("✅ FAQ Test Passed!")
            else:
                print("❌ FAQ Test Failed: Keyword not found in answer.")
        else:
            print(f"❌ API Error: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_api_faq()
