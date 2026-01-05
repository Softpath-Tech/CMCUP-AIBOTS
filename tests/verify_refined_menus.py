
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
    SESSION_STATE
)

async def verify_refined_menus():
    print("\n=== TEST: Refined Submenus ===\n")

    # 1. Registration Menu (Expanded to 5 options)
    print("--- Testing Registration Menu ---")
    SESSION_STATE["test_sess"] = MENU_MAIN
    resp = await process_user_query("1", "test_sess")
    txt = resp["response"]
    print(txt)
    
    expected = [
        "How to Register", "Eligibility Rules", "Documents Required", 
        "Registration Status", "FAQs"
    ]
    if all(k in txt for k in expected):
         print("✅ Registration Menu correct (5 options).")
    else:
         print("❌ Registration Menu mismatch.")

    # 2. Sports Menu (Renamed options)
    print("\n--- Testing Sports Menu ---")
    SESSION_STATE["test_sess"] = MENU_MAIN
    resp = await process_user_query("2", "test_sess")
    txt = resp["response"]
    print(txt)

    if "Sports Disciplines" in txt and "Schedules & Fixtures" in txt:
          print("✅ Sports Menu labels correct.")
    else:
          print("❌ Sports Menu labels mismatch.")

    # 3. Help Menu (Flattened)
    print("\n--- Testing Help Menu ---")
    SESSION_STATE["test_sess"] = MENU_MAIN
    resp = await process_user_query("5", "test_sess")
    txt = resp["response"]
    print(txt)

    if "Helpline Numbers" in txt and "Email Support" in txt:
           print("✅ Help Menu labels correct.")
    else:
           print("❌ Help Menu labels mismatch.")

if __name__ == "__main__":
    asyncio.run(verify_refined_menus())
