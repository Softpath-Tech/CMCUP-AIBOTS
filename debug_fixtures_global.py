from rag.data_store import get_datastore
import pandas as pd

def check_global_stats():
    ds = get_datastore()
    if not ds.initialized: ds.init_db()

    print("\n--- 1. Global Fixture Count ---")
    count = ds.query("SELECT count(*) as count FROM tb_fixtures").iloc[0]['count']
    print(f"Total rows in tb_fixtures: {count}")

    if count > 0:
        print("\n--- 2. Games WITH Fixtures ---")
        # Get unique disc_ids from fixtures and join with discipline name
        query = """
        SELECT DISTINCT f.disc_id, d.dist_game_nm 
        FROM tb_fixtures f
        LEFT JOIN tb_discipline d ON f.disc_id = d.game_id
        LIMIT 20
        """
        df = ds.query(query)
        print(df.to_string())

    print("\n--- 3. Kabaddi Specifics ---")
    df_kab = ds.query("SELECT * FROM tb_discipline WHERE LOWER(dist_game_nm) LIKE '%kabaddi%'")
    if not df_kab.empty:
        print(df_kab[['game_id', 'dist_game_nm']].to_string())
    else:
        print("No Kabaddi in tb_discipline")

if __name__ == "__main__":
    check_global_stats()
