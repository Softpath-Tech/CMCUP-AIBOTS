import requests
import json
import time

base_url = "http://localhost:8000"

def test_chat(query, session_id):
    print(f"\n🔹 TESTING /chat: '{query}' (Session: {session_id})")
    try:
        url = f"{base_url}/chat"
        payload = {"query": query, "session_id": session_id}
        # Increased timeout to 30s to debug RAG fallback vs Menu
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"🔸 Response Body:\n{data.get('response', 'No response field')}")
        print(f"🔸 Source: {data.get('source', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("🚀 Starting Rules & Fallthrough Verification (Retry)")
sid = "rules_test_002"

# 1. Start -> Main Menu
test_chat("Hi", sid)

# 2. Select Rules (4) -> Rules Menu
test_chat("4", sid)

# 3. Select Age Limit (1) -> Should ASK FOR SPORT
test_chat("1", sid)
