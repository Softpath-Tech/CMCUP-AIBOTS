
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
    MENU_GROUP_SPORTS,
    MENU_GROUP_VENUES,
    MENU_GROUP_HELP,
    SESSION_STATE
)

async def test_option(parent_menu_name, option_idx, description):
    # Reset state to parent menu
    session_id = f"test_{parent_menu_name}_{option_idx}"
    SESSION_STATE[session_id] = parent_menu_name
    
    print(f"\n🔹 Testing: {description} (Option {option_idx})")
    try:
        resp = await process_user_query(str(option_idx), session_id)
        txt = resp["response"]
        print(f"--- RESPONSE START ---\n{txt}\n--- RESPONSE END ---")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def verify_all():
    print("=== STARTING COMPREHENSIVE SUBMENU VERIFICATION ===\n")
    
    print("\n### 🏠 Main Menu Response")
    print(f"--- RESPONSE START ---\n{get_menu_text(MENU_MAIN)}\n--- RESPONSE END ---")

    # 1. Registration & Eligibility (MENU_REG_FAQ)
    # We must first navigate to it to ensure state validity, though test_option mocks state.
    # Options: 1. How to, 2. Eligibility, 3. Docs, 4. Status, 5. FAQs
    print("\n\n### 1️⃣ Registration & Eligibility Sub-options")
    await test_option(MENU_REG_FAQ, 1, "How to Register")
    await test_option(MENU_REG_FAQ, 2, "Eligibility Rules")
    await test_option(MENU_REG_FAQ, 3, "Documents Required")
    await test_option(MENU_REG_FAQ, 4, "Registration Status")
    await test_option(MENU_REG_FAQ, 5, "FAQs")

    # 2. Sports & Matches (MENU_GROUP_SPORTS)
    # Options: 1. Disciplines, 2. Schedules, 3. Medal Tally
    print("\n\n### 2️⃣ Sports & Matches Sub-options")
    await test_option(MENU_GROUP_SPORTS, 1, "Sports Disciplines")
    await test_option(MENU_GROUP_SPORTS, 2, "Schedules & Fixtures")
    await test_option(MENU_GROUP_SPORTS, 3, "Medal Tally")

    # 3. Venues & Officials (MENU_GROUP_VENUES)
    # Options: 1. Venues, 2. District Officers, 3. Venue In-Charge
    print("\n\n### 3️⃣ Venues & Officials Sub-options")
    await test_option(MENU_GROUP_VENUES, 1, "Venues")
    await test_option(MENU_GROUP_VENUES, 2, "District Officers")
    await test_option(MENU_GROUP_VENUES, 3, "Venue In-Charge")

    # 4. Player Status 
    # This is a direct menu, check its text.
    print("\n\n### 4️⃣ Player Status")
    # Simulate valid navigation to it
    SESSION_STATE["ps_test"] = MENU_MAIN
    resp = await process_user_query("4", "ps_test")
    print(f"--- RESPONSE START ---\n{resp['response']}\n--- RESPONSE END ---")

    if "Search by Phone No" in resp['response']:
         print("✅ Player Status Menu correct.")
    else:
         print("❌ Player Status Menu mismatch.")


    # 5. Help & Language (MENU_GROUP_HELP)
    # Options: 1. Helpline, 2. Email, 3. Language
    print("\n\n### 5️⃣ Help & Language Sub-options")
    await test_option(MENU_GROUP_HELP, 1, "Helpline Numbers")
    await test_option(MENU_GROUP_HELP, 2, "Email Support")
    await test_option(MENU_GROUP_HELP, 3, "Change Language")

if __name__ == "__main__":
    asyncio.run(verify_all())
