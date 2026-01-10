import asyncio
import sys
import os

# Ensure we can import api.main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import process_user_query, SESSION_STATE, SESSION_DATA, MENU_MAIN

async def reproduce():
    session_id = "test_ack_crash"
    
    # 1. Start Session
    print("\n--- Sending 'Hi' ---")
    await process_user_query("Hi", session_id)
    
    # 2. Send Ack No directly (mimicking user input)
    # Based on user report: "SATGCMC25-330200005"
    ack_no = "SATGCMC25-330200005"
    print(f"\n--- Sending Ack No: {ack_no} ---")
    
    # Force state if needed, but the logic might auto-detect "SATGCMC"
    # Let's inspect main.py to see if we need to be in a specific menu, 
    # but usually unique IDs are global or part of Player Status menu.
    # The user said "Search by Acknowledgment No", implying they might be in that menu.
    # Let's try navigating there first to be safe, or just sending it if it's a global detector.
    
    # Navigate to Player Status (Option 6 in Main Menu logic, usually)
    # Check main.py: Option 4 is Player Status
    
    print("--- Navigating to Player Status Menu ---", flush=True)
    SESSION_STATE[session_id] = "MENU_PLAYER_STATUS" # setting directly for speed
    
    try:
        resp = await process_user_query(ack_no, session_id)
        print(f"DEBUG: Response Type: {type(resp)}", flush=True)
        if resp:
             print(f"Bot Response: {resp.get('text')}", flush=True)
        else:
             print("❌ Response is None!", flush=True)
        
        if resp and ("Something went wrong" in resp.get('text', '') or "Error" in resp.get('text', '')):
            print("❌ Issue Reproduced: Crash or Generic Error detected.")
        else:
            print("✅ Issue Not Reproduced (or already handled).")
            
    except Exception as e:
        print(f"❌ CRASHED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reproduce())
