from rag.data_store import get_datastore

def check_khokho():
    ds = get_datastore()
    if not ds.initialized: ds.init_db()

    print("--- Checking Kho-Kho (ID 19) ---")
    query = """
    SELECT fixture_id, match_date, team1_dist_id, team2_dist_id 
    FROM tb_fixtures WHERE disc_id = 19 LIMIT 3
    """
    df = ds.query(query)
    if not df.empty:
        print("✅ Found Kho-Kho fixtures:")
        print(df.to_string())
    else:
        print("❌ Unexpected: No Kho-Kho fixtures found despite earlier check.")

if __name__ == "__main__":
    check_khokho()
