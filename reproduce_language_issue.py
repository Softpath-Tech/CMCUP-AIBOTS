import sys
import os
import asyncio
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import process_user_query, SESSION_DATA, SESSION_STATE

async def reproduce():
    print("🧪 Reproducing Static Language Issue")
    session_id = "repro_lang_001"
    
    # 1. Set Language to Hindi
    # Standard flow: Main -> Help (5) -> Language (3) -> Hindi (3)
    # Or shortcut: Manually set session data if we trust the flow, but let's do it via menu to be safe/realistic.
    
    await process_user_query("menu", session_id)
    await process_user_query("5", session_id) # Help
    await process_user_query("3", session_id) # Change Language
    await process_user_query("3", session_id) # Hindi
    
    print(f"Language set to: {SESSION_DATA.get(session_id, {}).get('language')}")
    
    # 2. Navigate to Registration (Option 1)
    # The main menu should now be in Hindi (due to previous fixes).
    resp_main = await process_user_query("menu", session_id)
    # We expect Hindi text here.
    
    # 3. Select "How to Register" (Option 1 inside Registration)
    # Main -> 1 (Registration)
    await process_user_query("1", session_id) 
    # Registration Menu -> 1 (How to Register)
    resp_static = await process_user_query("1", session_id)
    
    print(f"\nResponse for 'How to Register' (Hindi Context):")
    print(resp_static.get('text'))
    
    # Check if text contains English "To Register" or Hindi equivalent
    if "To Register" in resp_static.get('text', ''):
        print("❌ Issue Reproduced: Response is in English.")
    else:
        print("✅ Issue Not Reproduced: Response might be in Hindi (or unexpected).")

if __name__ == "__main__":
    asyncio.run(reproduce())
