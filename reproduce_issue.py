import sys
import os
import asyncio
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import process_user_query, SESSION_DATA, SESSION_STATE

async def reproduce():
    print("🧪 Reproducing Menu Structure Issue")
    session_id = "repro_struct_001"
    
    # 1. Start
    await process_user_query("menu", session_id)
    
    # 2. Navigate to Sports & Matches (Option 2)
    await process_user_query("2", session_id)
    
    # 3. Navigate to Sports Disciplines (Option 1)
    await process_user_query("1", session_id)
    
    # 4. Navigate to Cluster Level (Option 1)
    # Note: Depending on logic, this might return a list of sports
    resp_levels = await process_user_query("1", session_id)
    
    if not resp_levels.get("isMenusAvailable"):
        print("❌ Failed to get sports list at Cluster Level. Cannot proceed.")
        return

    print("✅ Got Sports List.")
    
    # 5. Select first sport (Option 1)
    # The user report says "Athletics", let's assume 1 is valid.
    resp_game = await process_user_query("1", session_id)
    
    print(f"\nResponse for Game Option 1:")
    print(json.dumps(resp_game, indent=2))
    
    # CHECK
    if "menus" in resp_game and len(resp_game["menus"]) > 0:
        print("\n✅ PASS: Response has menus.")
        # Optional: check button labels
        buttons = [b['name'] for b in resp_game['menus']]
        print(f"Buttons: {buttons}")
    else:
        print("\n❌ FAIL: Response is missing menus (unstructured).")

if __name__ == "__main__":
    asyncio.run(reproduce())
