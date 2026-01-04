import sys
import os
sys.path.append(os.getcwd())
from rag.data_store import get_datastore

def debug_check():
    ds = get_datastore()
    if not ds.initialized: ds.init_db()
    
    val = "cricket"
    q = f"SELECT * FROM view_sport_rules WHERE LOWER(sport_name) LIKE '%{val}%'"
    print(f"Running: {q}")
    df = ds.query(q)
    
    if df.empty:
        print("No matches found for cricket!")
    else:
        print(f"Found {len(df)} matches:")
        for _, row in df.iterrows():
            print(f"- {row['sport_name']} (Len: {len(row['sport_name'])})")

if __name__ == "__main__":
    debug_check()
