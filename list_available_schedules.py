from rag.data_store import get_datastore
import pandas as pd

def list_all_available():
    ds = get_datastore()
    if not ds.initialized: ds.init_db()

    query = """
    SELECT DISTINCT d.dist_game_nm 
    FROM tb_fixtures f
    JOIN tb_discipline d ON f.disc_id = d.game_id
    ORDER BY d.dist_game_nm
    """
    df = ds.query(query)
    
    if df.empty:
        print("No schedules found at all.")
    else:
        print("--- Sports with Available Schedules ---")
        for i, row in df.iterrows():
            print(f"{i+1}. {row['dist_game_nm']}")

if __name__ == "__main__":
    list_all_available()
