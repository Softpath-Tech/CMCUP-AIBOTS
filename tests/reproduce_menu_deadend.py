import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_menu_flow():
    session_id = str(uuid.uuid4())
    print(f"🆔 Session ID: {session_id}")
    
    # helper
    def send(text):
        print(f"\n📤 User: {text}")
        try:
            res = requests.post(f"{BASE_URL}/chat", json={"query": text, "session_id": session_id})
            res.raise_for_status()
            data = res.json()
            ans = data.get("response", "")
            print(f"📥 Bot: {ans[:300]}...")  # Truncate
            return ans
        except Exception as e:
            print(f"❌ Error: {e}")
            return ""

    # 1. Start - EXPECT Main Menu
    r1 = send("Hi")
    if "Welcome" not in r1:
        print("❌ FAIL: Did not get Main Menu")
        return
    
    # 2. Schedule - EXPECT Schedule Menu
    r2 = send("2")
    if "Match Schedules" not in r2:
        print("❌ FAIL: Did not get Schedule Menu")
        return

    # 3. By Sport - EXPECT Prompt "Which sport"
    r3 = send("1")
    if "Which sport" not in r3:
        print("❌ FAIL: Did not get Sport prompt")
        return

    # 4. Input "Cricket" - EXPECT Schedule Results (Fixing the dead end)
    r4 = send("Cricket")
    
    # Evaluation
    # If currently broken, it might return menu again, or fall back to RAG saying "I need more info" or just generic.
    # If fixed, it should say "Schedule for Cricket" or similar.
    
    if "Cricket Schedule" in r4 or "Team" in r4 or "vs" in r4 or "No specific schedule found" in r4:
        print("✅ PASS: Got actionable results for 'Cricket' via menu flow.")
    else:
        print("❌ FAIL: Did NOT get Cricket schedule. Likely loop or context loss.")
        print(f"Full Response: {r4}")

if __name__ == "__main__":
    test_menu_flow()
