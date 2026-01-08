import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = str(uuid.uuid4())

def chat(query):
    try:
        resp = requests.post(f"{BASE_URL}/chat", json={"query": query, "session_id": SESSION_ID})
        resp.raise_for_status()
        data = resp.json()
        # Handle structured response: {text, menus, ...}
        # Backward compatibility check if needed, but we know it's strict now.
        return data.get("text", "")
    except Exception as e:
        print(f"Error: {e}")
        return ""

def verify_language_flow():
    print(f"--- Starting Language Verification [Session: {SESSION_ID}] ---")

    # 1. Start -> English Default
    print("\n1. [Input: Hi] (Expect English Menu)")
    res = chat("Hi")
    print(f"Response start: {res[:50].replace('\n', ' ')}...")
    if "Welcome to Telangana" in res:
        print("✅ Default is English")
    else:
        print("❌ Default English Check Failed")

    # 2. Go to Language Menu
    print("\n2. [Input: 5] (Expect Help Menu)")
    res = chat("5")
    print(f"Response start: {res[:50].replace('\n', ' ')}...")
    
    print("\n3. [Input: 3] (Select Change Language)")
    res = chat("3")
    print(f"Response start: {res[:50].replace('\n', ' ')}...")

    # 3. Select Telugu
    print("\n4. [Input: 2] (Select Telugu)")
    res = chat("2")
    print(f"Response: {res}")
    if "తెలుగు" in res:
        print("✅ Language Change Acknowledged (Telugu)")
    else:
        print("❌ Language Change Check Failed")

    # 4. Check Menu in Telugu
    print("\n5. [Input: Menu] (Expect Telugu Menu)")
    res = chat("Menu")
    print(f"Response: {res}")
    if "తెలంగాణ ስపోర్ట్స్" in res or "తెలంగాణ" in res:
        print("✅ Menu is in Telugu")
    else:
        print("❌ Telugu Menu Check Failed")

    # 5. Check RAG/Question in Telugu (Mock/Instruction Check)
    # Note: Cannot fully verify LLM output deterministically without running LLM, 
    # but we can check if the system didn't crash.
    print("\n6. [Input: Kabaddi rules] (Expect Telugu Instruction/Response)")
    res = chat("Kabaddi rules")
    print(f"Response: {res[:100]}...")

    # 6. Switch back to English
    chat("5")
    chat("3")
    res = chat("1") # Select English
    print("\n7. Switched back to English.")
    
    res = chat("Menu")
    if "Welcome" in res:
        print("✅ Back to English confirmed")
    else:
        print("❌ Revert to English Failed")

if __name__ == "__main__":
    verify_language_flow()
