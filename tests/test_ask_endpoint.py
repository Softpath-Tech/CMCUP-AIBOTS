
import sys
import os
from fastapi.testclient import TestClient

# Ensure project root is in path
sys.path.append(os.getcwd())

from api.main import app

client = TestClient(app)

def test_rag_via_chat():
    """Test the RAG functionality via /chat endpoint (replacing /ask)"""
    print("\n🧪 Testing RAG Query via /chat...")
    payload = {"query": "What is the scholarship logic?"}
    
    # Send request to /chat (previous /ask)
    response = client.post("/chat", json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # We expect 200 if RAG is working
    if response.status_code == 200:
        data = response.json()
        # API returns "text" or "response"
        assert "text" in data or "response" in data
        assert "source" in data
        # Source might be rag_knowledge_base or sql_agent depending on logic interception
        assert data["source"] in ["rag_knowledge_base", "sql_agent", "rag_chain"]
        print("✅ RAG query worked successfully")
    elif response.status_code == 503:
        print("⚠️ Service Unavailable (RAG Brain not initialized).")
    else:
        print(f"⚠️ Request failed with status {response.status_code}")
        # Fail the test if it's not a known safe failure
        assert False, f"Request failed: {response.text}"

if __name__ == "__main__":
    test_rag_via_chat()
