from rag.data_store import get_datastore
import pandas as pd

def check_kabaddi():
    ds = get_datastore()
    if not ds.initialized: ds.init_db()

    print("--- 1. Checking tb_discipline for Kabaddi ---")
    df_disc = ds.query("SELECT * FROM tb_discipline WHERE LOWER(dist_game_nm) LIKE '%kabaddi%'")
    if df_disc.empty:
        print("❌ No 'Kabaddi' found in tb_discipline.")
        return
    else:
        print(f"✅ Found {len(df_disc)} entries in tb_discipline:")
        print(df_disc[['game_id', 'dist_game_nm']].to_string())
    
    # Check fixtures for each game_id found
    for _, row in df_disc.iterrows():
        game_id = row['game_id']
        game_name = row['dist_game_nm']
        print(f"\n--- 2. Checking fixtures for Game ID: {game_id} ({game_name}) ---")
        
        # Check raw count
        query_count = f"SELECT count(*) as count FROM tb_fixtures WHERE disc_id = {game_id}"
        count = ds.query(query_count).iloc[0]['count']
        print(f"Total fixtures found: {count}")
        
        if count > 0:
            query_fix = f"""
            SELECT fixture_id, match_no, venue, match_date, team1_dist_id, team2_dist_id, disc_id 
            FROM tb_fixtures WHERE disc_id = {game_id} LIMIT 5
            """
            df_fix = ds.query(query_fix)
            print(df_fix.to_string())

if __name__ == "__main__":
    check_kabaddi()
