import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from api.main import process_user_query, SESSION_STATE, MENU_MAIN

async def test_invalid_menu_option():
    # Setup session
    session_id = "test_sess_invalid_opt"
    SESSION_STATE[session_id] = MENU_MAIN
    
    # Simulate invalid input "99" (Main menu has only 1-5)
    print(f"\nSending invalid input '99' to Main Menu...")
    response = await process_user_query("99", session_id)
    
    print(f"Response Source: {response.get('source')}")
    print(f"Response Text: {response.get('response')}")
    
    # EXPECTATION: Should be caught by validation, NOT go to RAG
    # Currently it goes to RAG, so source might be 'rag_knowledge_base' or 'rag_chain'
    # We want it to be 'menu_system' or 'validation_error'
    
    if response.get('source') in ['menu_system', 'validation_error']:
        print("✅ SUCCESS: Invalid option caught correctly.")
    else:
        print("❌ FAILURE: Invalid option fell through to " + str(response.get('source')))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_invalid_menu_option())
