import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())

with patch.dict(sys.modules, {
    'rag.chain': MagicMock(),
    'rag.sql_queries': MagicMock(),
    'rag.location_search': MagicMock(),
    'rag.data_store': MagicMock(),
    'rag.sql_agent': MagicMock()
}):
    import api.main as main_api

async def debug_flow():
    session_id = "debug_sess"
    
    # 1. Setup Language
    print(f"--- 1. Set Lang ---")
    main_api.SESSION_DATA[session_id] = {"language": "te"}
    main_api.SESSION_STATE[session_id] = "MENU_MAIN"
    
    # Flow
    steps = ["1", "1.1", "back"]
    
    for q in steps:
        print(f"\nQUERY: {q}")
        print(f"PRE-STATE: {main_api.SESSION_STATE.get(session_id)}")
        resp = await main_api.process_user_query(q, session_id)
        print(f"POST-STATE: {main_api.SESSION_STATE.get(session_id)}")
        print(f"RESP: {resp.get('text')[:50]}...")

if __name__ == "__main__":
    asyncio.run(debug_flow())
