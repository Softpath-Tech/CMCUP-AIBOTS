
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def test_language_selection_failure():
    session_id = "test_lang_issue"
    
    # 1. Main Menu
    client.post("/chat", json={"query": "Hi", "session_id": session_id})
    
    # 2. Go to Help (Option 5)
    resp = client.post("/chat", json={"query": "5", "session_id": session_id})
    assert "Help & Language" in resp.json()["text"]
    
    # 3. Go to Language (Option 3)
    resp = client.post("/chat", json={"query": "3", "session_id": session_id})
    assert "Select Language" in resp.json()["text"]
    
    # 4. Select Telugu (Option 2) - This should fail currently
    resp = client.post("/chat", json={"query": "2", "session_id": session_id})
    data = resp.json()
    print(f"Response: {data.get('text', data)}")
    
    # We expect this to contain confirmation of Telugu selection (Main Menu in Telugu)
    if "స్వాగతం" in data.get("text", "") or "తెలంగాణ" in data.get("text", ""):
        print("SUCCESS: Language selection worked! Telugu content found.")
    else:
        print("FAILURE: Language selection failed. Content still English/Incorrect.")

if __name__ == "__main__":
    test_language_selection_failure()
