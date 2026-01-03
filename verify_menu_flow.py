import requests
import json
import uuid

API_URL = "http://localhost:8000/chat"
SESSION_ID = str(uuid.uuid4())

def chat(query):
    payload = {"query": query, "session_id": SESSION_ID}
    print(f"User: {query}")
    try:
        r = requests.post(API_URL, json=payload)
        r.raise_for_status()
        data = r.json()
        print(f"Bot: {data.get('response')}\n")
        return data.get('response')
    except Exception as e:
        print(f"Error: e")
        return ""

def test_disciplines_logic():
    print("=== Testing Disciplines Logic ===")
    
    # Levels to test: 1 (Cluster) -> 5 (State)
    levels = {
        "1": "Cluster", 
        "2": "Mandal", 
        "3": "Assembly", 
        "4": "District", 
        "5": "State"
    }
    
    for key, name in levels.items():
        print(f"\n--- Testing Level: {name} ({key}) ---")
        chat("Hi") # Reset
        chat("2")  # Select Disciplines
        resp = chat(key) # Select Level
        
        if "Sports at" in resp:
            lines = resp.split('\n')
            # Handle "1. SportName" or "- SportName"
            sports = []
            for l in lines:
                l = l.strip()
                if l and (l[0].isdigit() and ". " in l):
                    parts = l.split(". ", 1)
                    if len(parts) > 1:
                        sports.append(parts[1])
                elif l.startswith('- '):
                    sports.append(l[2:])
            
            print(f"Found {len(sports)} sports for {name}.")
            if len(sports) > 0:
                print(f"Sample: {sports[:3]}")
                
                 # DRILL DOWN TEST
                print(f"   -> Drilling down into Sport #1 ({sports[0]})...")
                chat("1") # Select first sport
                
                # Check Options Menu
                resp_opts = chat("1") # Select Age Criteria
                if "Age Criteria" in resp_opts:
                    print("   ✅ Age Criteria Loaded")
                else:
                    print(f"   ❌ Age Criteria Failed: {resp_opts[:50]}...")
                    
                chat("Back") # Back to Options
                chat("2") # Select Events
                # Expecting a URL
                chat("Back")
                chat("Back") # Back to List
        else:
            print(f"FAIL: No sports returned for {name}")

if __name__ == "__main__":
    test_disciplines_logic()
