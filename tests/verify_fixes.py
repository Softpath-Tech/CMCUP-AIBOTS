
import sys
import os
import asyncio

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import process_user_query, STATE_WAIT_DIST_OFFICER, STATE_WAIT_CLUSTER_INCHARGE, SESSION_STATE

async def verify_fixes():
    print("=== TEST: Final Logic Fixes ===\n")

    # 1. District Officer Formatting
    session_id_1 = "fix_test_1"
    SESSION_STATE[session_id_1] = STATE_WAIT_DIST_OFFICER
    print("Testing District Search Formatting ('Nalgonda')...")
    resp1 = await process_user_query("Nalgonda", session_id_1)
    
    txt1 = str(resp1["response"])
    print(f"   Response Preview: {txt1[:60]}...")
    
    if "{" in txt1 and "district_name" in txt1:
        print("   FAILED: Still returning raw dictionary.")
    elif "District Sports Officer - Nalgonda" in txt1:
        print("   SUCCESS: Formatting applied.")
    else:
        print(f"   WARNING: Unexpected output format: {txt1}")

    # 2. Cluster In-Charge 500 Fix
    session_id_2 = "fix_test_2"
    SESSION_STATE[session_id_2] = STATE_WAIT_CLUSTER_INCHARGE
    print("\nTesting Cluster Search 500 Fix ('ADILABAD')...")
    
    try:
        resp2 = await process_user_query("ADILABAD", session_id_2)
        txt2 = str(resp2["response"])
        print(f"   Response Preview: {txt2[:60]}...")
        
        if "Venue In-Charge" in txt2:
            print("   SUCCESS: Logic executed without crash.")
        else:
            print("   FAILED: Logic executed but returned unexpected.")
            
    except Exception as e:
        print(f"   FAILED: CRASHED with error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_fixes())
