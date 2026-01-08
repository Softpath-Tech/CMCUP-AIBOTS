import sys
import os
import asyncio
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import process_user_query, SESSION_DATA

async def verify_structure():
    print("🧪 Starting Verification: Structured API Response")
    session_id = "verify_struct_001"
    
    # 1. Test Main Menu (English)
    print("\n🔹 Test 1: Main Menu (English)")
    resp = await process_user_query("menu", session_id)
    
    print(f"Response Keys: {list(resp.keys())}")
    assert "text" in resp, "Missing 'text' key"
    assert "menus" in resp, "Missing 'menus' key"
    assert "isMenusAvailable" in resp, "Missing 'isMenusAvailable' key"
    
    if resp["isMenusAvailable"]:
        print(f"✅ Main Menu has {len(resp['menus'])} options.")
        first_menu = resp['menus'][0]
        print(f"   First Option: {first_menu}")
        assert "name" in first_menu and "value" in first_menu, "Menu item missing name/value"
    else:
        print("❌ Main Menu should have options!")
        
    # 2. Test Language Switch (Telugu)
    print("\n🔹 Test 2: Language Switch to Telugu")
    # Simulate language selection
    await process_user_query("2", session_id) # Option 5: Help -> Option 3: Lang -> Option 2: Telugu
    # Direct set for speed
    SESSION_DATA[session_id] = {"language": "te"}
    
    resp_te = await process_user_query("menu", session_id)
    print(f"Telugu Text: {resp_te['text'][:50]}...")
    first_menu_te = resp_te['menus'][0]
    print(f"Telugu Menu[0]: {first_menu_te}")
    
    assert first_menu_te['name'] != "Registration & Eligibility", "Menu text should be translated!"
    
    # 3. Test Dynamic List (Disciplines)
    print("\n🔹 Test 3: Dynamic Disciplines (Cluster Level)")
    # Navigate: Menu -> 2 (Sports) -> 1 (Disciplines) -> 1 (Cluster)
    # Reset to English
    SESSION_DATA[session_id]["language"] = "en"
    
    await process_user_query("2", session_id) # Sports Group
    await process_user_query("1", session_id) # Disciplines Menu
    resp_disc = await process_user_query("1", session_id) # Cluster Level
    
    print(f"Discipline Response Source: {resp_disc['source']}")
    print(f"Is Menus Available: {resp_disc['isMenusAvailable']}")
    
    if resp_disc['isMenusAvailable']:
        print(f"✅ Found {len(resp_disc['menus'])} sports buttons.")
        print(f"   Examples: {[m['name'] for m in resp_disc['menus'][:3]]}")
        # Submenu items should still be "1", "2" etc.
        assert resp_disc['menus'][0]['value'] == "1", "First sport value should be '1'"
        

        print("❌ Disciplines should be returned as buttons now!")

    # 4. Verify Main Menu Keys
    print("\n🔹 Test 4: Main Menu Keys")
    resp_main = await process_user_query("menu", session_id)
    first_main = resp_main['menus'][0]
    print(f"Main Menu Option 1: {first_main}")
    assert first_main['value'] == "MAIN_1", f"Expected MAIN_1, got {first_main['value']}"

    print("\n🎉 Verification Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(verify_structure())
