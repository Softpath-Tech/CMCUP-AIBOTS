
import sys
import os
import asyncio
import re

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import process_user_query

async def verify_queries():
    print("=== TEST: Phone Number Lookup Scenarios ===\n")

    # Scenario 1: User's number (Expect No Record found, but NO Privacy Block)
    user_phone = "9703662169"
    print(f"\n🔹 Scenario 1: User Input '{user_phone}' (Unknown Number)")
    resp1 = await process_user_query(user_phone, "sess_1")
    txt1 = resp1["response"]
    print(f"   Response: {txt1[:100]}...") # Print preview
    
    if "Privacy Notice" in txt1:
        print("   ❌ FAILED: Privacy Notice triggered.")
    elif "No registrations found" in txt1:
        print("   ✅ SUCCESS: Correctly returned 'No registrations found'.")
    else:
        print(f"   ⚠️ UNEXPECTED: {txt1}")

    # Scenario 2: Valid Database Number (Expect Details)
    db_phone = "7416613302"
    print(f"\n🔹 Scenario 2: DB Input '{db_phone}' (Valid Number)")
    resp2 = await process_user_query(db_phone, "sess_2")
    txt2 = resp2["response"]
    print(f"   Response Start:\n{txt2[:200]}...")
    
    if "Venue Details" in txt2 or "Player Details" in txt2 or "registrations for this number" in txt2:
        print("   ✅ SUCCESS: Returned Player/Venue details.")
    else:
        print(f"   ❌ FAILED: Did not return expected details. Got: {txt2}")

if __name__ == "__main__":
    asyncio.run(verify_queries())
