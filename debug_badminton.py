from rag.data_store import get_datastore
import pandas as pd

def check_badminton():
    ds = get_datastore()
    if not ds.initialized: ds.init_db()

    print("--- 1. Checking tb_discipline for Badminton ---")
    df_disc = ds.query("SELECT * FROM tb_discipline WHERE LOWER(dist_game_nm) LIKE '%badminton%'")
    
    if df_disc.empty:
        print("❌ No 'Badminton' found in tb_discipline.")
        return
    
    print(df_disc[['game_id', 'dist_game_nm']].to_string())

    for _, row in df_disc.iterrows():
        game_id = row['game_id']
        game_name = row['dist_game_nm']
        print(f"\n--- 2. Checking fixtures for Game ID: {game_id} ({game_name}) ---")
        
        query_count = f"SELECT count(*) as count FROM tb_fixtures WHERE disc_id = {game_id}"
        count = ds.query(query_count).iloc[0]['count']
        print(f"Total fixtures found: {count}")
        
        if count > 0:
            query_fix = f"SELECT * FROM tb_fixtures WHERE disc_id = {game_id} LIMIT 5"
            print(ds.query(query_fix).to_string())

if __name__ == "__main__":
    check_badminton()
