
import sys
import os
import asyncio
import traceback

# Mock project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import process_user_query, MENU_GROUP_VENUES, MENU_OFFICERS_DISTRICT, MENU_OFFICERS_CLUSTER, get_menu_text, SESSION_STATE

async def reproduce():
    print("=== REPRODUCING 500 ERROR IN VENUES MENU ===\n")
    
    print(f"Constant Check:")
    print(f"   MENU_OFFICERS_DISTRICT = {MENU_OFFICERS_DISTRICT}")
    print(f"   MENU_OFFICERS_CLUSTER = {MENU_OFFICERS_CLUSTER}")
    
    print(f"get_menu_text Check:")
    try:
        txt = get_menu_text(MENU_OFFICERS_DISTRICT)
        print(f"   get_menu_text(DISTRICT) = {txt[:50]}...")
    except Exception as e:
        print(f"   get_menu_text(DISTRICT) CRASHED: {e}")

    # Test District Officers (Option 2)
    session_id = "test_err_1"
    SESSION_STATE[session_id] = MENU_GROUP_VENUES
    print(f"Testing Option 2 (District Officers)...")
    try:
        resp = await process_user_query("2", session_id)
        print(f"   Response: {resp}")
    except Exception:
        print("   CRASH DETECTED:")
        traceback.print_exc()

    # Test Venue In-Charge (Option 3)
    session_id_2 = "test_err_2"
    SESSION_STATE[session_id_2] = MENU_GROUP_VENUES
    print(f"Testing Option 3 (Venue In-Charge)...")
    try:
        resp = await process_user_query("3", session_id_2)
        print(f"   Response: {resp}")
    except Exception:
        print("   CRASH DETECTED:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reproduce())
