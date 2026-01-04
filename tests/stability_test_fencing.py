import sys
import os
import asyncio
import pandas as pd

sys.path.append(os.getcwd())
from api.main import process_user_query, SESSION_STATE, MENU_MAIN

TEST_QUERIES = [
    # A. Hierarchy
    "Show all State Level Sports",
    "Is Fencing a State Level sport?",
    "List only Para Sports",
    
    # B. Discipline Specific
    "Tell me about Fencing", # General RAG?
    "Fencing Age Criteria", # Intent lookup
    
    # C. Age Criteria
    "What is the age limit for Fencing?",
    "Show age criteria for Fencing",
    
    # D. Events
    "What events are there in Fencing?",
    
    # E. Rules
    "Show rules of Fencing",
    "What are the rules for Fencing?",
    
    # I. Context (Sequence)
    ("SEQUENCE", [
        "What is Fencing?",
        "What is its age limit?", # Should infer Fencing
        "Show its rules"         # Should infer Fencing
    ])
]

async def run_tests():
    print("--- Starting Stability Test (Fencing) ---")
    results = []
    
    sess_id = "test_fencing_sess"
    
    for item in TEST_QUERIES:
        if isinstance(item, str):
            q = item
            print(f"\nQUERY: {q}")
            resp = await process_user_query(q, sess_id)
            print(f"   -> SOURCE: {resp.get('source')}")
            print(f"   -> RESP: {resp.get('response')[:100]}...")
            results.append({"query": q, "source": resp.get("source"), "response_preview": resp.get("response")[:50]})
        
        elif isinstance(item, tuple) and item[0] == "SEQUENCE":
            print(f"\n--- SEQUENCE TEST ---")
            SESSION_STATE[sess_id] = MENU_MAIN # Reset for fresh sequence? Or keep?
            # actually usually context implies keeping session.
            
            for q in item[1]:
                print(f"SEQ QUERY: {q}")
                resp = await process_user_query(q, sess_id)
                print(f"   -> SOURCE: {resp.get('source')}")
                print(f"   -> RESP: {resp.get('response')[:100]}...")

if __name__ == "__main__":
    asyncio.run(run_tests())
