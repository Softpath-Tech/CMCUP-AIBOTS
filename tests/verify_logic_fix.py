import sys
import os
import asyncio


# Add project root to path
sys.path.append(os.getcwd())

from api.main import process_user_query, SESSION_STATE, SESSION_DATA, MENU_MAIN, CHAT_SESSIONS

# Mock Data
SESSION_ID = "test_session_123"

async def test_logic():
    print("--- STARTING VERIFICATION ---")

    # 1. Test MAIN_2 Navigation (Simulate clicking 'Sports' from deep submenu)
    print("\n[TEST 1] Navigation Reset (MAIN_2)")
    # Set state to deep submenu
    SESSION_STATE[SESSION_ID] = "MENU_SOME_DEEP_STATE"
    
    # Send "MAIN_2" (Sports)
    response = await process_user_query("MAIN_2", SESSION_ID)
    
    # Check if state reset to correct submenu (MENU_GROUP_SPORTS) or fallen through
    # Logic: MAIN_2 -> splits to "2", State reset to MENU_MAIN.
    # Then falls through to digit logic: if state==MENU_MAIN and choice==2 -> MENU_GROUP_SPORTS
    
    current_state = SESSION_STATE.get(SESSION_ID)
    print(f"Result State: {current_state}")
    print(f"Response Text Prefix: {str(response['text'])[:50]}...")
    
    if current_state == "MENU_GROUP_SPORTS":
        print("✅ PASS: Navigation reset and routed correctly.")
    else:
        print(f"❌ FAIL: Expected MENU_GROUP_SPORTS, got {current_state}")

    # 2. Test Language Switch Redirect
    print("\n[TEST 2] Language Switch Redirect")
    # Reset to Menu Language
    SESSION_STATE[SESSION_ID] = "MENU_LANGUAGE"
    
    # Select 2 (Telugu)
    response = await process_user_query("2", SESSION_ID)
    
    # Expected: State reset to MENU_MAIN, text contains Telugu welcome
    current_state = SESSION_STATE.get(SESSION_ID)
    lang = SESSION_DATA.get(SESSION_ID, {}).get("language")
    
    print(f"Result State: {current_state}")
    print(f"Language: {lang}")
    print(f"Response Text Prefix: {str(response['text'])[:50]}...")
    
    if current_state == MENU_MAIN and lang == "te" and "స్వాగతం" in str(response['text']):
         print("✅ PASS: Language switched and redirected to Main Menu.")
    else:
         print(f"❌ FAIL: State={current_state}, Lang={lang}")

if __name__ == "__main__":
    # Mocking RECENT_HISTORY as it might be used
    if 'RECENT_HISTORY' not in globals():
        from api.main import CHAT_SESSIONS
    
    asyncio.run(test_logic())
