import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import process_user_query, SESSION_STATE

async def test_menu_structure():
    print("🚀 Starting Menu Structure Verification...")
    session_id = "test_sess_001"
    
    # 1. Main Menu
    print("\n--- Testing Main Menu ---")
    res = await process_user_query("menu", session_id)
    menu_txt = res["response"]
    print(menu_txt)
    assert "**1. Registration & Eligibility**" in menu_txt
    assert "**5. Help & Language**" in menu_txt
    
    # 2. Registration Menu (Option 1)
    print("\n--- Testing Registration Menu ---")
    res = await process_user_query("1", session_id)
    reg_txt = res["response"]
    print(reg_txt)
    assert "**1. Registration & Eligibility**" in reg_txt
    assert "1.1 How to Register" in reg_txt
    assert "1.5 FAQs" in reg_txt
    
    await process_user_query("back", session_id)

    # 3. Sports Menu (Option 2)
    print("\n--- Testing Sports Menu ---")
    res = await process_user_query("2", session_id)
    sport_txt = res["response"]
    print(sport_txt)
    assert "**2. Sports & Matches**" in sport_txt
    assert "2.1 Sports Disciplines" in sport_txt
    assert "2.3 Medal Tally" in sport_txt

    await process_user_query("back", session_id)

    # 4. Venues Menu (Option 3)
    print("\n--- Testing Venues Menu ---")
    res = await process_user_query("3", session_id)
    venue_txt = res["response"]
    print(venue_txt)
    assert "**3. Venues & Officials**" in venue_txt
    assert "3.1 Venues" in venue_txt
    assert "3.3 Venue In-Charge" in venue_txt
    assert "3.4 Mandal In-Charge" in venue_txt # Should be PRESENT now
    
    await process_user_query("back", session_id)

    # 5. Player Status (Option 4)
    print("\n--- Testing Player Status Menu ---")
    res = await process_user_query("4", session_id)
    player_txt = res["response"]
    print(player_txt)
    assert "**4. Player Status**" in player_txt
    assert "4.1 Search by Phone No" in player_txt
    
    await process_user_query("back", session_id)

    # 6. Help Menu (Option 5)
    print("\n--- Testing Help Menu ---")
    res = await process_user_query("5", session_id)
    help_txt = res["response"]
    print(help_txt)
    assert "**5. Help & Language**" in help_txt
    assert "5.1 Helpline Numbers" in help_txt
    assert "5.3 Change Language" in help_txt

    print("\n✅ Verification Passed!")

if __name__ == "__main__":
    asyncio.run(test_menu_structure())
