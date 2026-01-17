import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
PHONE_NUMBER = "919703662169"

def send_whatsapp_msg(msg):
    url = f"{BASE_URL}/whatsappchat"
    payload = {
        "user_message": msg,
        "first_name": "Test User",
        "phone_number": PHONE_NUMBER
    }
    resp = requests.post(url, json=payload)
    print(f"\n[USER]: {msg}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"[BOT]: {data.get('text', 'NO RESPONSE')}")
        return data
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
        return None

def test_flow():
    print("--- Starting Automated Phone Search Test ---")
    
    # 1. Reset to Main Menu
    send_whatsapp_msg("home")
    
    # 2. Go to Player Status (Option 4)
    send_whatsapp_msg("4")
    
    # 3. Select Search by Phone No (Option 1)
    # This should now return details immediately instead of a prompt.
    resp = send_whatsapp_msg("1")
    
    if resp and ("Search Results" in resp.get("text", "") or "Player Details" in resp.get("text", "") or "Found" in resp.get("text", "")):
        print("\n✅ SUCCESS: Automated phone search worked!")
    elif resp and "Please enter your registered Mobile Number" in resp.get("text", ""):
        print("\n❌ FAILURE: Still showing prompt instead of results.")
    else:
        print("\n❓ UNKNOWN: Response received but didn't match expected success/failure indicators.")
        print(f"Full response: {resp}")

if __name__ == "__main__":
    test_flow()
