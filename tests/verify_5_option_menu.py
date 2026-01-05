
import sys
import os
import asyncio

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import (
    process_user_query, 
    get_menu_text,
    MENU_MAIN,
    MENU_GROUP_SPORTS,
    MENU_GROUP_VENUES,
    MENU_GROUP_HELP,
    SESSION_STATE
)

async def verify_menu_flow():
    print("\n=== TEST: 5-Option Main Menu Flow ===\n")
    
    # 1. Main Menu Content
    main_text = get_menu_text(MENU_MAIN)
    print("Main Menu:\n", main_text)
    if "1️⃣ Registration" in main_text and "5️⃣ Help" in main_text:
        print("✅ Main Menu content looks correct (5 options).")
    else:
        print("❌ Main Menu content mismatch.")

    # 2. Verify Option 2: Sports & Matches (Group)
    print("\n--- Testing Option 2 (Sports & Matches) ---")
    SESSION_STATE["test_sess"] = MENU_MAIN
    resp = await process_user_query("2", "test_sess")
    txt = resp["response"]
    print(txt)
    
    if "Disciplines" in txt and "Schedules" in txt and "Medal Tally" in txt:
        print("✅ Menu Group Sports correct.")
    else:
        print("❌ Menu Group Sports mismatch.")

    # 3. Verify Option 3: Venues & Officials (Group)
    print("\n--- Testing Option 3 (Venues & Officials) ---")
    SESSION_STATE["test_sess"] = MENU_MAIN
    resp = await process_user_query("3", "test_sess")
    txt = resp["response"]
    print(txt)
    
    if "Venues Information" in txt and "District Officers" in txt and "Venue In-Charge" in txt:
        print("✅ Menu Group Venues correct.")
    else:
        print("❌ Menu Group Venues mismatch.")

    # 4. Verify Option 5: Help & Language (Group)
    print("\n--- Testing Option 5 (Help & Language) ---")
    SESSION_STATE["test_sess"] = MENU_MAIN
    resp = await process_user_query("5", "test_sess")
    txt = resp["response"]
    print(txt)
    
    if "Helpdesk" in txt and "Language" in txt:
        print("✅ Menu Group Help correct.")
    else:
        print("❌ Menu Group Help mismatch.")

if __name__ == "__main__":
    asyncio.run(verify_menu_flow())
