import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import process_user_query, SESSION_STATE, SESSION_DATA, get_menu_data, MENU_SELECT_SPORT

async def run_test():
    session_id = "test_level_switch_1"
    
    # 1. Start: Select Mandal Level (LEVEL_2)
    print("--- 1. Selecting Mandal Level (LEVEL_2) ---")
    resp = await process_user_query("LEVEL_2", session_id)
    
    # Check State
    print(f"State: {SESSION_STATE.get(session_id)}")
    if SESSION_STATE.get(session_id) != MENU_SELECT_SPORT:
        print("❌ FAILED: Did not enter MENU_SELECT_SPORT")
        return

    # Check Data
    sports = SESSION_DATA[session_id].get("sports", [])
    print(f"Mandal Sports Count: {len(sports)}")
    if "Football" in sports:
        print("❌ ERROR: Football shouldn't be in Mandal list (based on previous check)")
    else:
        print("✅ Correct: Football not in Mandal list")

    # 2. Switch: Select District Level (LEVEL_4)
    print("\n--- 2. Switching to District Level (LEVEL_4) ---")
    resp = await process_user_query("LEVEL_4", session_id)
    
    print(f"Response Text Prefix: {resp['text'][:50]}...")
    
    # Check Data Update
    sports_new = SESSION_DATA[session_id].get("sports", [])
    print(f"District Sports Count: {len(sports_new)}")
    
    if "Football" in sports_new:
        print("✅ SUCCESS: Football is in District list!")
    else:
        print("❌ FAILED: Football NOT in District list. Data did not update!")
        print(f"Current List: {sports_new[:5]}...")

if __name__ == "__main__":
    asyncio.run(run_test())
