
import sys
import os
import asyncio

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import (
    process_user_query, 
    get_menu_text,
    MENU_MAIN,
    MENU_REG_FAQ,
    MENU_DISCIPLINES,
    MENU_SCHEDULE,
    MENU_VENUES,
    MENU_OFFICERS,
    MENU_PLAYER_STATUS,
    MENU_MEDALS,
    MENU_HELPDESK,
    MENU_LANGUAGE,
    SESSION_STATE
)

def test_main_menu_options():
    print("\n=== TEST: Main Menu Options ===")
    main_text = get_menu_text(MENU_MAIN)
    
    # Check for expected number of options visually (1-9)
    if "9️⃣" in main_text:
        print("✅ Main Menu appears to have 9 options.")
    else:
        print("❌ Main Menu might be missing options.")

async def verify_submenu(option_num, menu_name, expected_content_keywords):
    print(f"\n=== TEST: Option {option_num} ({menu_name}) ===")
    
    # Simulate user selecting the option from Main Menu
    session_id = f"sess_opt_{option_num}"
    SESSION_STATE[session_id] = MENU_MAIN
    
    # Send input '1', '2', etc.
    resp = await process_user_query(str(option_num), session_id)
    menu_txt = resp["response"]
    
    print(f"Response for Option {option_num}:\n{menu_txt}")
    
    # Check if ANY of the keywords match
    if isinstance(expected_content_keywords, str):
        expected_content_keywords = [expected_content_keywords]
        
    found = False
    for kw in expected_content_keywords:
        if kw.lower() in menu_txt.lower():
            found = True
            break
            
    if found:
        print(f"✅ Option {option_num} seems correct (Matched keyword).")
        return True
    else:
        print(f"❌ Option {option_num} MISMATCH! Expected one of '{expected_content_keywords}'.")
        return False

async def run_tests():
    test_main_menu_options()
    
    # 1. Registration FAQ
    await verify_submenu(1, "Registration FAQ", "Registration")
    
    # 2. Disciplines
    await verify_submenu(2, "Disciplines", "Select Level")
    
    # 3. Schedules
    await verify_submenu(3, "Schedules", ["Tournament Schedule", "Games Schedule", "Schedules"])
    
    # 4. Venues
    await verify_submenu(4, "Venues", ["Data coming soon", "Venues"])
    
    # 5. Officers (New)
    await verify_submenu(5, "Officers", ["District Officers", "Officers"])
    
    # 6. Player Status (Fixed)
    await verify_submenu(6, "Player Status", ["Player Details", "Acknowledgment"])
    
    # 7. Medals
    await verify_submenu(7, "Medals", "Medal Tally")
    
    # 8. Helpdesk
    await verify_submenu(8, "Helpdesk", "Helpdesk")
    
    # 9. Language
    await verify_submenu(9, "Language", ["Select Language", "Language"])

if __name__ == "__main__":
    asyncio.run(run_tests())
