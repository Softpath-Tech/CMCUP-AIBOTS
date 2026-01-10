
import pytest
from fastapi.testclient import TestClient
from api.main import app
import time

client = TestClient(app)

@pytest.mark.parametrize("question, lang_label", [
    ("What is the address of the Sports Authority?", "English"),
    ("Sports Authority ka address kya hai?", "Hindi"),
    # ("Who is the CM of Telangana?", "English"),
    # ("Telangana ka CM kaun hai?", "Hindi"),
    # ("Telangana CM evaru?", "Telugu"),
])
def test_question(question, lang_label):
    print(f"\n[{lang_label}] Asking: {question}")
    
    start = time.time()
    # Use /chat endpoint as /ask seems missing or deprecated, and main.py uses /chat
    response = client.post("/chat", json={"query": question})
    lat = time.time() - start
    
    assert response.status_code == 200
    
    data = response.json()
    # Handle mixed API response format (text vs response)
    ans = data.get("text") or data.get("response") or data.get("answer", "")
    model = data.get("model_used", "Unknown") # Might not be present in all responses
    
    print(f"✅ Response ({lat:.2f}s) [Model: {model}]: {ans}\n")
    assert ans is not None and len(str(ans)) > 0
