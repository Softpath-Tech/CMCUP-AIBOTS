
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def test_menu_flow():
    session_id = "test_session_001"
    
    # 1. Main Menu (Start)
    resp = client.post("/chat", json={"query": "Hi", "session_id": session_id})
    assert resp.status_code == 200
    data = resp.json()
    ans = data.get("text") or data.get("response") or ""
    menus = data.get("menus") or []
    
    print(f"Response 1: {ans}")
    assert "Welcome to Telangana Sports Authority" in ans
    
    # Check for button presence
    # Button names should be in the menus list
    button_names = [b.get("name") for b in menus]
    assert "Registration & Eligibility" in button_names

    # 2. Navigate to Player Status (Option 4)
    # Note: Main menu Option 4 is "Player Status"
    resp = client.post("/chat", json={"query": "4", "session_id": session_id})
    data = resp.json()
    ans = data.get("text") or data.get("response") or ""
    menus = data.get("menus") or []
    
    print(f"Response 2: {ans}")
    assert "Player Status" in ans
    
    button_names = [b.get("name") for b in menus]
    assert "Search by Phone No" in button_names

    # 3. Sub-menu Navigation (Option 1 -> Search by Phone)
    resp = client.post("/chat", json={"query": "1", "session_id": session_id})
    data = resp.json()
    ans = data.get("text") or data.get("response") or ""
    
    print(f"Response 3: {ans}")
    assert "Mobile Number" in ans or "Phone No" in ans

    # 4. Back Navigation
    resp = client.post("/chat", json={"query": "Back", "session_id": session_id})
    data = resp.json()
    ans = data.get("text") or data.get("response") or ""
    menus = data.get("menus") or []
    
    print(f"Response 4: {ans}")
    assert "Player Status" in ans # Back to Player Status
    
    # 5. Back to Main
    resp = client.post("/chat", json={"query": "Back", "session_id": session_id})
    data = resp.json()
    ans = data.get("text") or data.get("response") or ""
    assert "Welcome to Telangana Sports Authority" in ans

def test_unknown_input_in_menu():
    session_id = "test_session_002"
    # Start
    client.post("/chat", json={"query": "Hi", "session_id": session_id})
    
    # Invalid Option
    resp = client.post("/chat", json={"query": "99", "session_id": session_id})
    data = resp.json()
    ans = data.get("text") or data.get("response") or ""
    print(f"Response Invalid: {ans}")
    # Verify it handles it gracefully
    assert resp.status_code == 200

if __name__ == "__main__":
    try:
        test_menu_flow()
        print("test_menu_flow PASSED")
        test_unknown_input_in_menu()
        print("test_unknown_input_in_menu PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        exit(1)
