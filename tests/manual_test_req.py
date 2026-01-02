import requests
import json
import time

base_url = "http://localhost:8000"

def test_chat(query, session_id):
    print(f"\n🔹 TESTING /chat: '{query}' (Session: {session_id})")
    try:
        url = f"{base_url}/chat"
        payload = {"query": query, "session_id": session_id}
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        print(f"🔸 Response Body:\n{data.get('response', 'No response field')}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("🚀 Starting Language Flow Verification (Retry)")
sid = "lang_test_002"

# 1. Reset (Should show Language Menu)
test_chat("Hi", sid)

# 2. Select English (Should go to Main Menu)
test_chat("1", sid)
