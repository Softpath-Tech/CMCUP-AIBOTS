import sys
import os
import asyncio
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import process_user_query, SESSION_STATE, SESSION_DATA, save_sessions, load_sessions, MENU_SCHEDULE_GAME_SEARCH, MENU_GROUP_VENUES

async def run_tests():
    print("🚀 STARTING FINAL VERIFICATION 🚀\n")
    
    # -------------------------------------------------
    # 1. TEST LOCALIZATION PERSISTENCE
    # -------------------------------------------------
    print("--- 1. Testing Session Persistence ---")
    sid = "test_sess_persist"
    SESSION_DATA[sid] = {"language": "hi"}
    save_sessions()
    
    # Simulate Restart (Clear Memory)
    SESSION_DATA.clear()
    load_sessions()
    
    if SESSION_DATA.get(sid, {}).get("language") == "hi":
        print("✅ PASS: Language 'hi' persisted after reload.")
    else:
        print(f"❌ FAIL: Language lost. Found: {SESSION_DATA.get(sid)}")

    # -------------------------------------------------
    # 2. TEST GAMES SCHEDULE LOOKUP
    # -------------------------------------------------
    print("\n--- 2. Testing Games Schedule Lookup ---")
    sid_sched = "test_sched"
    SESSION_STATE[sid_sched] = MENU_SCHEDULE_GAME_SEARCH
    
    # Test with a known game (e.g., Kabaddi or Athletics - assuming data exists)
    # If no data, it handles gracefully. We just want to check it doesn't crash or return empty.
    resp = await process_user_query("Kabaddi", sid_sched)
    if "Schedule for Kabaddi" in resp["text"] or "No schedule found" in resp["text"]:
         print("✅ PASS: Schedule Lookup executed correctly.")
    else:
         print(f"❌ FAIL: Unexpected response for Schedule: {resp['text'][:50]}...")

    # -------------------------------------------------
    # 3. TEST VENUES LEVELS & FALLBACK
    # -------------------------------------------------
    print("\n--- 3. Testing Venues Level & Fallback ---")
    sid_ven = "test_venue"
    # Testing VENUE_LEVEL_4 (District)
    # Should either give venues or Fallback to Officer
    resp = await process_user_query("VENUE_LEVEL_4", sid_ven)
    
    is_venue_list = "Venues for District Level" in resp["text"]
    is_fallback = "District Sports Officer's" in resp["text"]
    
    if is_venue_list or is_fallback:
        print(f"✅ PASS: Venue Level logic worked. (Result Type: {'List' if is_venue_list else 'Fallback'})")
    else:
        print(f"❌ FAIL: Venue logic failed. Response: {resp['text'][:50]}...")

    # -------------------------------------------------
    # 4. TEST NLQ: OFFICER LOOKUP
    # -------------------------------------------------
    print("\n--- 4. Testing NLQ: Warangal Officer ---")
    sid_nlq = "test_nlq"
    resp = await process_user_query("Warangal Officer", sid_nlq)
    
    if "District Sports Officer Details" in resp["text"] and "Warangal" in resp["text"]:
        print("✅ PASS: NLQ 'Warangal Officer' resolved correctly.")
    else:
        print(f"❌ FAIL: NLQ failed. Response: {resp['text'][:50]}...")

if __name__ == "__main__":
    asyncio.run(run_tests())
