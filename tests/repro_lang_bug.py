import sys
import os
import asyncio

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import process_user_query, SESSION_STATE, SESSION_DATA, get_menu_data
from rag.translations import MENU_TRANSLATIONS

async def run_test():
    session_id = "test_lang_user_1"
    
    print("--- 1. Set Language to Hindi (Option 3 in Menu 5) ---")
    # Simulate flow: Main -> Help -> Level 3 (Hindi)? 
    # Actually Help Menu is Global 5.
    # User flow: "Change Language" -> "Hindi"
    
    # 1. Force state to MENU_LANGUAGE (skip nav steps for brevity)
    SESSION_STATE[session_id] = "MENU_LANGUAGE"
    # Select 3 (Hindi)
    resp = await process_user_query("3", session_id)
    print(f"Set Lang Response: {resp['text'][:50]}...")
    
    lang = SESSION_DATA[session_id].get("language")
    print(f"Stored Language: {lang}")
    if lang != "hi":
        print("❌ FAILED to set language in session")
        return

    print("\n--- 2. Access Registration Menu (Option 1 from Main) ---")
    # State should have reset to MENU_MAIN by the language handler code
    print(f"State: {SESSION_STATE.get(session_id)}") # Should be MENU_MAIN
    
    resp = await process_user_query("1", session_id) # Option 1: Registration
    print(f"Reg Menu Response: {resp['text'][:50]}...")
    
    if "पंजीकरण" not in resp['text']:
        print("❌ FAILED: Menu 1 is not in Hindi!")
    else:
        print("✅ Menu 1 is in Hindi")

    print("\n--- 3. Select 'How to Register' (Option 1) ---")
    resp = await process_user_query("1", session_id)
    print(f"HowTo Response: {resp['text']}")
    
    if "पंजीकरण के लिए" in resp['text']:
        print("✅ SUCCESS: Found Hindi Response")
    else:
        print("❌ FAILED: Response is NOT in Hindi")
        print(f"Expected: 'पंजीकरण के लिए', Got: {resp['text']}")
        
    # Check what get_translation returns manually
    from rag.translations import get_translation
    t = get_translation("TXT_REG_HOWTO", "hi")
    print(f"\nManual Lookup 'TXT_REG_HOWTO' + 'hi': {t['text']}")

if __name__ == "__main__":
    asyncio.run(run_test())
