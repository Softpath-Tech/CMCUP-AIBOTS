from rag.data_store import get_datastore

def check_fencing():
    ds = get_datastore()
    ds.init_db()
    
    # Check Discipline
    df = ds.query("SELECT * FROM tb_discipline WHERE dist_game_nm LIKE '%Fencing%'")
    print("--- Fencing in tb_discipline ---")
    print(df)
    
    # Check Age Rules (View)
    df_rules = ds.query("SELECT * FROM view_sport_rules WHERE sport_name LIKE '%Fencing%'")
    print("\n--- Fencing in view_sport_rules ---")
    print(df_rules)

if __name__ == "__main__":
    check_fencing()
