import sys
import os
import asyncio
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import process_user_query, SESSION_DATA, SESSION_STATE

async def reproduce():
    print("🧪 Reproducing District Officer Issues")
    session_id = "repro_dist_002"
    
    # 1. Setup: Go to District Officers Menu
    # Main -> 3 (Venues) -> 2 (District Officers)
    print("\n--- Setup Navigation ---")
    await process_user_query("menu", session_id)
    await process_user_query("3", session_id)
    await process_user_query("2", session_id)
    
    # Check State
    print(f"Current State: {SESSION_STATE.get(session_id)}")
    
    # 2. Test Issue 1: Sequential Lookup
    print("\n--- Test Issue 1: Sequential Lookup ---")
    print("User: Warangal")
    resp1 = await process_user_query("Warangal", session_id)
    print(f"Bot 1: {resp1.get('text')[:50]}...")
    
    print(f"State after 1st query: {SESSION_STATE.get(session_id)}")
    
    print("User: Khammam")
    resp2 = await process_user_query("Khammam", session_id)
    print(f"Bot 2: {resp2.get('text')[:50]}...")
    
    if "error" in str(resp2).lower() or "wrong" in str(resp2).lower():
        print("❌ Issue 1 Reproduced: Second lookup failed.")
    else:
        print("✅ Issue 1 Not Reproduced: Second lookup worked.")

    # 3. Test Issue 2: NLQ in Menu
    print("\n--- Test Issue 2: NLQ 'Warangal Incharge' ---")
    # Reset state to waiting for officer logic manually for test purity or navigate again
    # Let's navigate again to be sure
    await process_user_query("menu", session_id)
    await process_user_query("3", session_id)
    await process_user_query("2", session_id)
    
    print("User: Warangal Incharge")
    resp3 = await process_user_query("Warangal Incharge", session_id)
    # detailed print
    print(json.dumps(resp3, indent=2))
    
    if "No District Sports Officer found" in resp3.get('text', '') or "could not be found" in resp3.get('text', ''):
        print("❌ Issue 2 Reproduced: Failed to handle 'Warangal Incharge'.")
    elif "District Sports Officer - Warangal" in resp3.get('text', ''):
        print("✅ Issue 2 Not Reproduced: Correctly handled NLQ.")
    else:
        print("⚠️ Unclear result for Issue 2.")

if __name__ == "__main__":
    asyncio.run(reproduce())
