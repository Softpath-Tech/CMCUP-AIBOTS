import asyncio
from api.main import process_user_query, SESSION_STATE, SESSION_DATA

async def test_global_nav():
    session_id = "test_glob_nav"
    SESSION_STATE.clear()
    if session_id in SESSION_DATA: del SESSION_DATA[session_id]

    print("--- 1. Start Session ---")
    resp = await process_user_query("Hi", session_id)
    print(f"Bot: {resp['text'][:50]}...")
    print(f"Bot: {resp['text'][:50]}...")
    print(f"Buttons: {resp.get('menus')}")
    assert "Registration" in resp['text'] or "1" in str(resp.get('menus', [])), "Main menu should have numeric options"
    
    print("\n--- 2. Enter Sports Menu (Send '2') ---")
    resp = await process_user_query("2", session_id)
    print(f"Bot: {resp['text'][:50]}...")
    buttons = resp.get('menus', [])
    print(f"Buttons: {[b['value'] for b in buttons]}")
    assert any("2.1" in b['value'] for b in buttons), "Sports menu should have 2.1, 2.2..."
    
    print("\n--- 3. Global Jump: '1.1' (How to Register) ---")
    # We are in Sports menu, but we type 1.1
    resp = await process_user_query("1.1", session_id)
    print(f"Bot: {resp['text'][:100]}...")
    assert "https://satg.telangana.gov.in" in resp['text'], "Should contain registration link"
    
    print("\n--- 4. Global Jump: '3.2' (District Officers) ---")
    resp = await process_user_query("3.2", session_id)
    print(f"Bot: {resp['text'][:100]}...")
    assert "District Name" in resp['text'], "Should ask for District Name"
    # Verify state update
    print(f"Current State: {SESSION_STATE.get(session_id)}")
    assert SESSION_STATE.get(session_id) == "STATE_WAIT_DIST_OFFICER", "State should be updated"

    print("\n--- 5. Global Jump: '4.2' (Ack No) ---")
    resp = await process_user_query("4.2", session_id)
    print(f"Bot: {resp['text'][:100]}...")
    assert "Acknowledgment Number" in resp['text'], "Should ask for Ack No"

    print("\n✅ Global Navigation Verification Passed!")

if __name__ == "__main__":
    asyncio.run(test_global_nav())
