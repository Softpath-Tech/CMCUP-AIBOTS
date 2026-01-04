import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:8000"

def run_test():
    session_id = str(uuid.uuid4())
    print(f"🆔 Session: {session_id}\n")

    def send(text, expected_keywords=[], context_name=""):
        print(f"👉 [{context_name}] User: {text}")
        try:
            res = requests.post(f"{BASE_URL}/chat", json={"query": text, "session_id": session_id}, timeout=30) # Increased timeout for RAG
            res.raise_for_status()
            r = res.json()
            ans = r.get("response", "")
            src = r.get("source", "")
            print(f"   🤖 Bot [{src}]: {ans[:100].replace(chr(10), ' ')}...")
            
            passed = True
            missing = []
            for k in expected_keywords:
                if k.lower() not in ans.lower():
                    passed = False
                    missing.append(k)
            
            if passed:
                print("   ✅ PASS")
            else:
                print(f"   ❌ FAIL. Missing: {missing}")
            return ans
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return ""

    print("--- 1. Main Menu & Navigation ---")
    send("Hi", ["Welcome", "Player Registration"], "Start")
    
    # Schedule Flow (Continuous Querying)
    print("\n--- 2. Schedule Flow (Context + Continuous) ---")
    send("2", ["Match Schedules", "1"], "Menu: Schedule")
    send("1", ["Which sport"], "Sub: By Sport")
    send("Kabaddi", ["Kabaddi", "Schedule"], "Input: Sport 1") 
    send("Cricket", ["Cricket", "Schedule"], "Input: Sport 2 (Continuous)") # Should work now!
    send("Back", ["Match Schedules"], "Nav: Back to Schedule Menu")
    send("Back", ["Welcome"], "Nav: Back to Main")

    # Rules Flow (Continuous Querying)
    print("\n--- 3. Rules Flow (Context + Continuous) ---")
    send("4", ["Sports Rules", "Age Limit"], "Menu: Rules")
    send("1", ["Which Sport"], "Sub: Age Limit")
    send("Judo", ["Rules for Judo"], "Input: Sport 1") # RAG
    # send("Boxing", ["Rules for Boxing"], "Input: Sport 2") # RAG - skip to save time/tokens if needed, but good to test.
    send("Back", ["Sports Rules"], "Nav: Back to Rules Menu")
    send("Back", ["Welcome"], "Nav: Back to Main")

    # Location (New Explicit State)
    print("\n--- 5. Location (Explicit State) ---")
    send("7", ["Location Verification", "Village"], "Menu: Location")
    send("Medipally", ["Location Found", "Mandal", "District"], "Input: Village Name")
    send("XyzVillage", ["could not be found", "Type another"], "Input: Invalid Village")
    send("Back", ["Location Verification"], "Nav: Back to Location Menu")
    send("Back", ["Welcome"], "Nav: Back to Main")

if __name__ == "__main__":
    run_test()
