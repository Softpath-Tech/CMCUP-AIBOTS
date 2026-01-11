import sys
import os
import asyncio

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import process_user_query, SESSION_STATE, SESSION_DATA, get_discipline_response

async def run_test():
    session_id = "test_user_123"
    
    print("--- 1. Start Session ---")
    await process_user_query("hi", session_id)
    print(f"State: {SESSION_STATE.get(session_id)}")
    
    print("\n--- 2. Select Disciplines (Option 2) ---")
    await process_user_query("2", session_id) # MENU_GROUP_SPORTS
    await process_user_query("1", session_id) # MENU_DISCIPLINES
    print(f"State: {SESSION_STATE.get(session_id)}")
    
    print("\n--- 3. Select Mandal Level (LEVEL_2) ---")
    resp = await process_user_query("LEVEL_2", session_id)
    print(f"State: {SESSION_STATE.get(session_id)}")
    print(f"Response: {resp['text'][:100]}...") # Check title
    
    # Verify Data
    data = SESSION_DATA.get(session_id, {})
    print(f"Level Title: {data.get('level_title')}")
    print(f"Sports Count: {len(data.get('sports', []))}")
    
    print("\n--- 4. Select District Level (LEVEL_4) ---")
    resp = await process_user_query("LEVEL_4", session_id)
    print(f"State: {SESSION_STATE.get(session_id)}")
    print(f"Response: {resp['text'][:100]}...") 
    
    # Verify Data update
    data = SESSION_DATA.get(session_id, {})
    title = data.get('level_title')
    print(f"Level Title: {title}")
    
    if "District" in title:
        print("✅ SUCCESS: Switched to District Level")
    else:
        print("❌ FAILURE: Did not switch to District Level")

if __name__ == "__main__":
    asyncio.run(run_test())
