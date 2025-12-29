from rag.data_store import get_datastore

def search_players_sql(value, search_type="mobile"):
    ds = get_datastore()
    if not ds.initialized:
        ds.init_db()

    # Note: player_details likely has 'vill_gp_name'. 
    # Link logic: vill_gp_name -> villagemaster.villagename
    # villagemaster has cluster_id -> clustermaster.cluster_id
    
    query = """
    SELECT 
        p.player_nm,
        p.player_reg_id,
        p.mobile_no,
        p.gender,
        p.player_age,
        p.vill_gp_name,
        
        -- Cluster Info
        c.clustername,
        c.incharge_name as cluster_incharge,
        c.mobile_no as incharge_mobile,

        -- Event/Game Info
        e.event_name,
        f.venue,
        f.match_date,
        f.match_time,
        f.match_day

    FROM player_details p
    
    -- Link Village -> Cluster
    LEFT JOIN villagemaster v ON TRIM(LOWER(p.vill_gp_name)) = TRIM(LOWER(v.villagename))
    LEFT JOIN clustermaster c ON v.cluster_id = c.cluster_id
    
    -- Link Event -> Fixture
    LEFT JOIN tb_events e ON p.event_id = e.id
    LEFT JOIN tb_fixtures f ON e.discipline_id = f.disc_id

    WHERE 
    """
    
    params = ()
    if search_type == "mobile":
        query += " p.mobile_no = ?"
        params = (str(value),)
    elif search_type == "reg_id":
        query += " (p.player_reg_id = ? OR p.id = ?)"
        params = (str(value), str(value))
    
    df = ds.query(query, params)
    
    if df.empty:
        return []
    
    return df.to_dict(orient="records")

def get_fixture_details(fixture_id):
    """
    Lookup match schedule using Fixture ID or Match No.
    Schema Update: districtmaster uses 'districtno' and 'districtname'.
    """
    ds = get_datastore()
    if not ds.initialized: ds.init_db()
    
    query = """
    SELECT 
        f.fixture_id,
        f.match_no,
        f.venue,
        f.match_date,
        f.match_time,
        f.match_day,
        f.round_name,
        f.team1_dist_id,
        f.team2_dist_id,
        d1.districtname as team1_name,
        d2.districtname as team2_name
    FROM tb_fixtures f
    LEFT JOIN districtmaster d1 ON f.team1_dist_id = d1.districtno
    LEFT JOIN districtmaster d2 ON f.team2_dist_id = d2.districtno
    WHERE f.fixture_id = ? OR f.match_no = ?
    """
    df = ds.query(query, (str(fixture_id), str(fixture_id)))
    
    if df.empty:
        return None
        
    return df.to_dict(orient="records")[0]

def get_geo_details(name):
    """
    Fuzzy search for District/Mandal/Village.
    Schema Update: 
    - districtmaster: districtname
    - mandalmaster: mandalname, districtno
    - villagemaster: villagename, distno, mandalno
    """
    ds = get_datastore()
    if not ds.initialized: ds.init_db()
    
    name_clean = name.strip().lower()
    
    # 1. District
    q_dist = "SELECT * FROM districtmaster WHERE LOWER(districtname) LIKE ?"
    df_dist = ds.query(q_dist, (f"%{name_clean}%",))
    if not df_dist.empty:
        # Normalize keys for output
        d = df_dist.to_dict(orient="records")[0]
        # map districtname to dist_nm for consistency if needed, or just use districtname
        return {"type": "District", "data": {"dist_nm": d.get('districtname')}}
        
    # 2. Mandal
    q_mand = "SELECT * FROM mandalmaster WHERE LOWER(mandalname) LIKE ?"
    df_mand = ds.query(q_mand, (f"%{name_clean}%",))
    if not df_mand.empty:
         m = df_mand.to_dict(orient="records")[0]
         m['mandal_nm'] = m.get('mandalname') # Normalize
         
         # Find parent district
         # mandalmaster uses districtno
         d_res = ds.query("SELECT districtname FROM districtmaster WHERE districtno = ?", (m.get('districtno'),))
         if not d_res.empty:
             m['parent_district'] = d_res.iloc[0]['districtname']
         return {"type": "Mandal", "data": m}

    # 3. Village
    q_vill = "SELECT * FROM villagemaster WHERE LOWER(villagename) LIKE ?"
    df_vill = ds.query(q_vill, (f"%{name_clean}%",))
    if not df_vill.empty:
        v = df_vill.to_dict(orient="records")[0]
        v['vill_nm'] = v.get('villagename')
        
        # Enrich from Master Tables (Authoritative) using distno/mandalno
        # villagemaster uses distno (not districtno)
        d_res = ds.query("SELECT districtname FROM districtmaster WHERE districtno = ?", (v.get('distno'),))
        
        # mandalmaster uses districtno and mandalno? Or just mandalno? 
        # Usually mandalno is unique per district.
        # mandalmaster columns: ID,DistrictNo,MandalName... implies compound key or unique mandalno?
        # Let's assume (districtno, mandalno) key.
        # villagemaster uses distno, mandalno.
        
        m_res = ds.query("SELECT mandalname FROM mandalmaster WHERE districtno = ? AND mandalno = ?", 
                         (v.get('distno'), v.get('mandalno')))
        
        if not d_res.empty: v['parent_district'] = d_res.iloc[0]['districtname']
        if not m_res.empty: v['parent_mandal'] = m_res.iloc[0]['mandalname']
        
        # Fallback to internal columns if join failed
        if 'parent_district' not in v and 'dist_nm' in v: v['parent_district'] = v['dist_nm']
        if 'parent_mandal' not in v and 'mandal_nm' in v: v['parent_mandal'] = v['mandal_nm']
        
        return {"type": "Village", "data": v}
        
    return None

def get_sport_schedule(sport_name):
    """
    Get all matches/events for a specific sport.
    Join tb_events and tb_fixtures.
    """
    ds = get_datastore()
    if not ds.initialized: ds.init_db()
    
    # 1. Find Discipline ID from tb_discipline or guess based on name?
    # Actually tb_events has discipline_id.
    # Let's search tb_events for event_name or sport name.
    
    # Check tb_events for matches
    # tb_events: id, event_name, event_description, discipline_id...
    # tb_fixtures: fixture_id, disc_id, venue...
    
    query = """
    SELECT 
        f.fixture_id,
        f.match_no,
        f.venue,
        f.match_date,
        f.match_time,
        f.round_name,
        d1.districtname as team1_name,
        d2.districtname as team2_name,
        e.event_name
    FROM tb_fixtures f
    JOIN tb_events e ON f.disc_id = e.discipline_id
    LEFT JOIN districtmaster d1 ON f.team1_dist_id = d1.districtno
    LEFT JOIN districtmaster d2 ON f.team2_dist_id = d2.districtno
    WHERE LOWER(e.event_name) LIKE ? OR LOWER(f.venue) LIKE ?
    LIMIT 10
    """
    # Simple fuzzy search on event name or venue
    q_str = f"%{sport_name.strip().lower()}%"
    df = ds.query(query, (q_str, q_str))
    
    if df.empty:
        return []
        
    return df.to_dict(orient="records")


def get_disciplines_by_level(level_name):
    """
    Get list of disciplines (games) played at a specific level.
    Based on is_level_code in tb_discipline.
    Mapping (inferred):
    1: Cluster Level
    2: Mandal Level
    3: District/State Level
    """
    ds = get_datastore()
    if not ds.initialized: ds.init_db()
    
    level_map = {
        "cluster": 1,
        "mandal": 2,
        "district": 3,
        "state": 3 
    }
    
    code = level_map.get(level_name.lower().strip())
    if not code:
        return []
        
    query = "SELECT dist_game_nm FROM tb_discipline WHERE is_level_code = ?"
    df = ds.query(query, (code,))
    
    if df.empty:
        return []
        
    return df['dist_game_nm'].tolist()
