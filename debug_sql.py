from rag.data_store import get_datastore

def debug():
    ds = get_datastore()
    ds.init_db()
    
    print("\n--- Raw Data Check ---")
    df = ds.query("SELECT dist_game_nm, is_level_code FROM tb_discipline LIMIT 5")
    print(df)
    
    print("\n--- Cast Check ---")
    try:
        df2 = ds.query("SELECT dist_game_nm, is_level_code FROM tb_discipline WHERE CAST(is_level_code AS INTEGER) <= 3")
        print(f"Rows found with CAST <= 3: {len(df2)}")
        print(df2.head())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug()
