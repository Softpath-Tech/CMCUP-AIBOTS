
import sys
import os
import asyncio

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import (
    process_user_query, 
    MENU_PLAYER_STATUS, 
    SESSION_STATE,
    STATE_WAIT_ACK,
    STATE_WAIT_PHONE
)

async def verify_player_menu():
    print("=== TEST: Player Status Menu Routing ===\n")

    # Test Option 1 (Phone)
    session_id_1 = "test_p1"
    SESSION_STATE[session_id_1] = MENU_PLAYER_STATUS
    print(f"Testing Option 1 (Phone)...")
    resp1 = await process_user_query("1", session_id_1)
    print(f"   Response: {resp1['response'][:100]}...")
    
    if SESSION_STATE.get(session_id_1) == STATE_WAIT_PHONE:
         print("   SUCCESS: State set to STATE_WAIT_PHONE")
    else:
         print(f"   FAILED: State is {SESSION_STATE.get(session_id_1)}")

    # Test Option 2 (Ack)
    session_id_2 = "test_p2"
    SESSION_STATE[session_id_2] = MENU_PLAYER_STATUS
    print(f"Testing Option 2 (Ack No)...")
    resp2 = await process_user_query("2", session_id_2)
    print(f"   Response: {resp2['response'][:100]}...")
    
    if SESSION_STATE.get(session_id_2) == STATE_WAIT_ACK:
         print("   SUCCESS: State set to STATE_WAIT_ACK")
    else:
         print(f"   FAILED: State is {SESSION_STATE.get(session_id_2)}")

if __name__ == "__main__":
    asyncio.run(verify_player_menu())
