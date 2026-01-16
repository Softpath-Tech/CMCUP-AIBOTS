import sys
import os
import re

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from api.main import (
    process_user_query, 
    SESSION_DATA, 
    SESSION_STATE, 
    MENU_MAIN, 
    MENU_GROUP_SPORTS, 
    MENU_DISCIPLINES,
    MENU_SELECT_SPORT,
    MENU_GAME_OPTIONS,
    MENU_REG_FAQ,
    MENU_SCHEDULE
)
from rag.translations import MENU_TRANSLATIONS

import asyncio

async def run_deep_check():
    session_id = "test_deep_consistency_te"
    # Force Telugu
    SESSION_DATA[session_id] = {"language": "te"}
    SESSION_STATE[session_id] = MENU_MAIN
    
    print("\n🚀 Starting Deep Consistency Check (Telugu)...\n")
    
    # 1. Main Menu -> Sports (2)
    print("[1] Navigating: Main Menu -> Sports (Input: '2')")
    resp_2 = await process_user_query("2", session_id)
    text_2 = resp_2["text"]
    assert "క్రీడలు" in text_2 or "Sports" in text_2, f"Expected Telugu Header/Content, got: {text_2[:50]}..."
    
    # 2. Sports -> Disciplines (2.1)
    print("\n[2] Navigating: Sports -> Disciplines (Input: '1')")
    resp_2_1 = await process_user_query("1", session_id)
    text_2_1 = resp_2_1["text"]
    
    print(f"   -> Response: {text_2_1[:100]}...")
    if "జిల్లా స్థాయి" not in text_2_1:
         print("❌ FAIL: 'District Level' not localized in Disciplines Menu")
    else:
         print("✅ PASS: Disciplines Menu Localized")

    # 3. Disciplines -> District Level (Input: '4')
    print("\n[3] Navigating: Disciplines -> District Level (Input: '4')")
    resp_lvl = await process_user_query("4", session_id)
    text_lvl = resp_lvl["text"]
    print(f"   -> Response: {text_lvl[:50]}...")
    
    if "క్రీడలు" not in text_lvl:
        print("❌ FAIL: Header 'Sports at...' not localized")
    else:
        print("✅ PASS: Sport List Header Localized")
        
    if "దిగువన ఉన్న క్రీడను ఎంచుకోండి" not in text_lvl:
         print("❌ FAIL: Prompt 'Select a sport below' not localized")
    else:
         print("✅ PASS: Sport Selection Prompt Localized")

    # 4. Select a Sport (Input: '1') -> Assume 'Athletics' or similar
    print("\n[4] Selecting Sport (Input: '1')")
    resp_sport = await process_user_query("1", session_id)
    text_sport = resp_sport["text"]
    print(f"   -> Response: {text_sport[:50]}...")
    
    buttons = resp_sport.get("menus", [])
    btn_names = [b["name"] for b in buttons]
    print(f"   -> Buttons: {btn_names}")
    
    has_telugu_btn = any(ord(c) > 128 for btn in btn_names for c in btn)
    if not has_telugu_btn:
        print("⚠️ WARNING: Sport Sub-Options (Age/Rules) seem to be in English. (Check main.py implementation)")
    else:
        print("✅ PASS: Sport Options Buttons Localized")

    # 5. Queries within Submenu
    print("\n[5] Querying Rules (Input: '3')")
    resp_rules = await process_user_query("3", session_id)
    text_rules = resp_rules["text"]
    print(f"   -> Response Head: {text_rules[:100]}...")
    
    if "The rulebook is currently being updated" in text_rules: 
         if "updated" in text_rules:
             print("❌ FAIL: Rules Query fallback is Hardcoded English")
         else:
             print("✅ PASS: Rules Query fallback appears localized")

if __name__ == "__main__":
    try:
        asyncio.run(run_deep_check())
    except Exception as e:
        print(f"\n💥 CRITICAL: Test Crashed: {e}")
        import traceback
        traceback.print_exc()
