
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def test_mandal_incharge_flow():
    session_id = "test_mandal_flow"
    
    # 1. Main Menu
    client.post("/chat", json={"query": "Hi", "session_id": session_id})
    
    # 2. Navigate to Venues (Option 3)
    resp = client.post("/chat", json={"query": "3", "session_id": session_id})
    assert "Venues & Officials" in resp.json()["response"]
    
    # 3. Select Mandal In-Charge (Option 4)
    resp = client.post("/chat", json={"query": "4", "session_id": session_id})
    data = resp.json()
    assert "Mandal Level In-Charge" in data["response"]
    assert "Please enter the **Mandal Name**" in data["response"]
    
    # 4. Enter Valid Mandal Name (e.g. "Jainad")
    # Using Jainad from our inspection earlier
    resp = client.post("/chat", json={"query": "Jainad", "session_id": session_id})
    data = resp.json()
    print(f"Response: {data['response']}")
    assert "Mandal In-Charge (MEO)" in data["response"]
    assert "G SRINIVAS" in data["response"] # Name from our inspection
    assert "6301501820" in data["response"] # Mobile from our inspection

def test_mandal_incharge_not_found():
    session_id = "test_mandal_404"
    client.post("/chat", json={"query": "Hi", "session_id": session_id})
    client.post("/chat", json={"query": "3", "session_id": session_id})
    client.post("/chat", json={"query": "4", "session_id": session_id})
    
    # Invalid Name
    resp = client.post("/chat", json={"query": "NonExistentMandalXYZ", "session_id": session_id})
    data = resp.json()
    assert "No Mandal In-Charge found" in data["response"]

if __name__ == "__main__":
    # Manually run if needed
    test_mandal_incharge_flow()
    print("Test Valid Flow Passed")
    test_mandal_incharge_not_found()
    print("Test Not Found Flow Passed")
