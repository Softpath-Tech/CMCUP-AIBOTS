import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import process_user_query

async def test_nlq_officer():
    print("🚀 Testing NLQ Officer Lookup...")
    session_id = "test_nlq_001"
    
    # Test Case 1: Direct "Incharge for [District]" query
    query = "Who is the incharge for Warangal"
    print(f"\n❓ Query: {query}")
    res = await process_user_query(query, session_id)
    print(f"✅ Response:\n{res['response']}")
    
    if "District Sports Officer" in res['response'] and "Warangal" in res['response']:
        print("Pass: Found Officer details.")
    else:
        print("Fail: Did not find officer details.")
    
    # Test Case 2: "District Officer [District]"
    query = "Khammam district officer"
    print(f"\n❓ Query: {query}")
    res = await process_user_query(query, session_id)
    print(f"✅ Response:\n{res['response']}")
    
    if "District Sports Officer" in res['response'] and "Khammam" in res['response']:
        print("Pass: Found Officer details.")
    else:
        print("Fail: Did not find officer details.")

if __name__ == "__main__":
    asyncio.run(test_nlq_officer())
