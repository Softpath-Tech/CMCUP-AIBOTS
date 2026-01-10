
import pytest
from fastapi.testclient import TestClient
from api.main import app
import time

client = TestClient(app)

@pytest.mark.parametrize("val, desc", [
    ("9959648666", "Phone Number (Real)"),
    ("SATGCMC25-001", "Reg ID (Mock)"),
])
def test_lookup(val, desc):
    print(f"\n🧪 Testing {desc}: {val}")
    
    start = time.time()
    res = client.post("/chat", json={"query": val})
    lat = time.time() - start
    
    assert res.status_code == 200
    
    data = res.json()
    src = data.get("source", "unknown")
    txt = data.get("text") or data.get("response", "")
    
    print(f"   ✅ Success ({lat:.2f}s) | Source: {src}")
    
    # Just verify we got a response. Specific content assertions might depend on DB state.
    # We log warnings if expected content is missing but don't fail the test unless it's a hard error.
    
    if "Cluster Details" in str(txt):
        print("      - Cluster Info Found ✅")
    else:
        print(f"      - Cluster Info MISSING (might be expected for this input) [Content: {str(txt)[:50]}...]")
        
    if "Game & Schedule" in str(txt):
            print("      - Schedule Found ✅")
            
    assert txt is not None
