import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import process_user_query

async def reproduce():
    query = "Who is the Mandal Incharge of Jainad"
    print(f"Testing Query: '{query}'")
    
    response = await process_user_query(query, session_id="repro_session")
    
    print("\n--- RESPONSE ---")
    print(response)
    
    if "G SRINIVAS" in str(response) or "6301501820" in str(response):
        print("\nSUCCESS: Found Mandal Incharge details.")
    else:
        print("\nFAILURE: Did NOT find Mandal Incharge details.")

if __name__ == "__main__":
    asyncio.run(reproduce())
