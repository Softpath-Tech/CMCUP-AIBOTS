
import sys
import os
import asyncio

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import process_user_query

async def verify_phone_lookup():
    print("=== TEST: Phone Number Lookup (Privacy Guardrail Check) ===\n")

    # User provided number
    phone = "9703662169"
    print(f"🔹 Testing Input: '{phone}'")
    
    # We pass None as session_id to treat it as a fresh query or general query
    # However the logic doesn't depend on session_id for this specific fallback block
    resp = await process_user_query(phone, "test_privacy_fix")
    txt = resp["response"]
    
    print(f"--- RESPONSE START ---\n{txt}\n--- RESPONSE END ---")

    if "Privacy Notice" in txt:
        print("❌ FAILED: Privacy Notice still triggered.")
    elif "No registrations found" in txt or "Venue Details" in txt:
        print("✅ SUCCESS: Guardrail bypassed. Lookup attempted.")
    else:
        print("⚠️ UNKNOWN RESPONSE: Check output.")

if __name__ == "__main__":
    asyncio.run(verify_phone_lookup())
