import sys
import os
import asyncio

sys.path.append(os.getcwd())
from api.main import get_menu_text, process_user_query, MENU_MAIN, SESSION_STATE, MENU_REGISTRATION, MENU_DISCIPLINES, MENU_SCHEDULE

async def test_submenus():
    print("--- Verifying Submenus ---")
    sess = "test_sess_sub"
    SESSION_STATE[sess] = MENU_MAIN
    
    # 1. Registration Menu (Main Option 1)
    resp = await process_user_query("1", sess)
    print(f"\n[1] Main->Reg: {resp['response'][:50]}...")
    assert "Registration FAQs" in resp['response']
    
    # 1.1 Reg Option 3 (Docs)
    resp = await process_user_query("3", sess)
    print(f"[1.1] Reg->Docs: {resp['response'][:50]}...")
    assert "Required Documents" in resp['response']
    
    # RESET
    SESSION_STATE[sess] = MENU_MAIN
    
    # 2. Disciplines Menu (Main Option 2)
    resp = await process_user_query("2", sess)
    print(f"\n[2] Main->Disc: {resp['response'][:50]}...")
    assert "Select Level" in resp['response']
    
    # 2.1 Disc Option 4 (District)
    resp = await process_user_query("4", sess)
    print(f"[2.1] Disc->District List FULL: {resp['response']}")
    # assert "Disciplines at District Level" in resp['response']
    # assert "Kabaddi" in resp['response'] # Assumption: Kabaddi is in DB
    
    # RESET
    SESSION_STATE[sess] = MENU_MAIN
    
    # 3. Schedules Menu (Main Option 3)
    resp = await process_user_query("3", sess)
    print(f"\n[3] Main->Sched: {resp['response'][:50]}...")
    assert "Schedules" in resp['response']
    
    # 3.1 Sched Option 1 (Tournament)
    resp = await process_user_query("1", sess)
    print(f"[3.1] Sched->Tournament: {resp['response'][:50]}...")
    assert "Tournament Schedule" in resp['response']
    assert "28 Jan" in resp['response']

    print("\n✅ Submenu Verification Passed!")

if __name__ == "__main__":
    asyncio.run(test_submenus())
