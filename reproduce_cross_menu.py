import sys
import os
import asyncio
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import process_user_query, SESSION_DATA, SESSION_STATE, MENU_DISCIPLINES, MENU_DISCIPLINES_LEVEL

async def reproduce():
    print("🧪 Reproducing Cross-Menu Navigation Issue")
    session_id = "repro_cross_001"
    
    # 1. Main Setup
    await process_user_query("menu", session_id)
    # 2 -> Sports & Matches
    await process_user_query("2", session_id)
    # 1 -> Sports Disciplines (MENU_DISCIPLINES)
    # Options: 1=Gram, 2=Mandal, 3=District, 4=State, 5=National
    await process_user_query("1", session_id)
    
    print(f"Current State: {SESSION_STATE.get(session_id)}")
    
    # 2. Select Mandal Level (Option 2)
    print("\n--- User Selects: LEVEL_2 (Mandal Level) ---")
    resp_mandal = await process_user_query("LEVEL_2", session_id)
    print(f"Bot Response (Snippet): {resp_mandal.get('text')[:100]}...")
    print(f"State after Mandal: {SESSION_STATE.get(session_id)}")
    
    # 3. Simulate Scroll Up & Click District Level (Option 4 - New Button)
    # The user sends "LEVEL_4" (District).
    print("\n--- User Selects: LEVEL_4 (District Level - New Button) ---")
    resp_district = await process_user_query("LEVEL_4", session_id)
    print(f"Bot Response (Snippet): {resp_district.get('text')[:100]}...")
    
    # Check if response contains "District" AND source is SQL (not RAG)
    if "District" in resp_district.get('text', '') and resp_district.get('source') == 'sql_database':
        print("✅ Issue Fixed: Correctly switched to District (SQL Source).")
    else:
        print(f"❌ Issue Failed: Response: {resp_district.get('text')} [Source: {resp_district.get('source')}]")

if __name__ == "__main__":
    asyncio.run(reproduce())
