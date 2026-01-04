import requests
import json

base_url = "http://localhost:8000"

def test_query(query):
    print(f"\n🔹 Querying: '{query}'")
    try:
        url = f"{base_url}/chat"
        # Not sending session_id to avoid menu trap, or sending a 'fresh' one
        payload = {"query": query, "session_id": "test_disciplines_001"}
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"🔸 Response Body:\n{data.get('response', 'No response field')}")
        print(f"🔸 Source: {data.get('source', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("🚀 Starting Discipline Data Verification")
# Use natural language to bypass menu (Menu trap handles specific digits/keywords)
# "disciplines at mandal level" usually hits the regex lookup if 'disciplines' keyword is present.
test_query("What are the disciplines available at Mandal Level?")
test_query("List sports at District Level")
