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
        
        -- Location Info
        v.villagename as vill_gp_name,
        
        -- Cluster Info
        c.clustername,
        c.incharge_name as cluster_incharge,
        c.mobile_no as incharge_mobile,

        -- Event/Game Info
        e.event_name,
        d.dist_game_nm as sport_name,
        f.venue,
        f.match_date,
        f.match_time,
        f.match_day,
        
        -- Level Info
        sp.is_mandal_level,
        sp.is_district_level,
        sp.is_state_level

    FROM player_details p
    
    -- Link Village -> Cluster (Using IDs)
    LEFT JOIN villagemaster v ON p.village_id = v.id
    LEFT JOIN clustermaster c ON v.cluster_id = c.cluster_id
    
    -- Link Game/Event Data
    LEFT JOIN tb_discipline d ON p.game_id = d.game_id
    LEFT JOIN tb_events e ON p.event_id = e.id

    -- Link Selection Levels
    LEFT JOIN tb_selected_players sp ON p.id = sp.player_id

    -- Link Fixture (Using Game ID + Gender + District)
    LEFT JOIN tb_fixtures f ON 
        p.game_id = f.disc_id 
        AND p.gender = f.gender
        AND (p.district_id = f.team1_dist_id OR p.district_id = f.team2_dist_id)

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

def get_participation_stats():
    """
    Returns total number of players registered.
    """
    try:
        ds = get_datastore()
        if not ds.initialized:
            ds.init_db()
            
        query = "SELECT COUNT(*) as total FROM player_details"
        df = ds.query(query)
        
        if df.empty:
            return 0
            
        return df.iloc[0]['total']
    except Exception as e:
        print(f"Error in get_participation_stats: {e}")
        return 0

def get_fixture_details(fixture_id):
    """
    Lookup match schedule using Fixture ID or Match No.
    Schema Update: districtmaster uses 'districtno' and 'districtname'.
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
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
    except Exception as e:
        print(f"Error in get_fixture_details for '{fixture_id}': {e}")
        return None

def get_geo_details(name):
    """
    Fuzzy search for District/Mandal/Village.
    Schema Update: 
    - districtmaster: districtname
    - mandalmaster: mandalname, districtno
    - villagemaster: villagename, distno, mandalno
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
        name_clean = name.strip().lower()
    
        # 1. District
        q_dist = "SELECT * FROM districtmaster WHERE LOWER(districtname) LIKE ?"
        df_dist = ds.query(q_dist, (f"%{name_clean}%",))
        if not df_dist.empty:
            d = df_dist.to_dict(orient="records")[0]
            return {"type": "District", "data": {"dist_nm": d.get('districtname')}}
        
        # 2. Mandal
        q_mand = "SELECT * FROM mandalmaster WHERE LOWER(mandalname) LIKE ?"
        df_mand = ds.query(q_mand, (f"%{name_clean}%",))
        if not df_mand.empty:
            m = df_mand.to_dict(orient="records")[0]
            m['mandal_nm'] = m.get('mandalname')
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
            d_res = ds.query("SELECT districtname FROM districtmaster WHERE districtno = ?", (v.get('distno'),))
            m_res = ds.query("SELECT mandalname FROM mandalmaster WHERE districtno = ? AND mandalno = ?", 
                             (v.get('distno'), v.get('mandalno')))
            if not d_res.empty: v['parent_district'] = d_res.iloc[0]['districtname']
            if not m_res.empty: v['parent_mandal'] = m_res.iloc[0]['mandalname']
            if 'parent_district' not in v and 'dist_nm' in v: v['parent_district'] = v['dist_nm']
            if 'parent_mandal' not in v and 'mandal_nm' in v: v['parent_mandal'] = v['mandal_nm']
            return {"type": "Village", "data": v}
        
        return None
    except Exception as e:
        print(f"Error in get_geo_details for '{name}': {e}")
        return None

def get_sport_schedule(sport_name):
    """
    Get all matches/events for a specific sport.
    1. Lookup game_id from tb_discipline.
    2. Query tb_fixtures by disc_id.
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
        info = get_discipline_info(sport_name)
        if not info:
            return []
        
        game_id = info['game_id']
        game_name = info['dist_game_nm']
        
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
            ? as sport_name
        FROM tb_fixtures f
        LEFT JOIN districtmaster d1 ON f.team1_dist_id = d1.districtno
        LEFT JOIN districtmaster d2 ON f.team2_dist_id = d2.districtno
        WHERE f.disc_id = ?
        ORDER BY f.match_date, f.match_time
        LIMIT 15
        """
        
        df = ds.query(query, (game_name, game_id))
        
        if df.empty:
            return []
            
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error in get_sport_schedule for '{sport_name}': {e}")
        return []


def get_fixture_sports():
    """
    Returns a sorted list of sport names that currently have fixtures.
    Useful for suggesting alternatives when a sport has no schedule yet.
    """
    try:
        ds = get_datastore()
        if not ds.initialized:
            ds.init_db()

        # Get unique disc_id values that have fixtures
        df_ids = ds.query("SELECT DISTINCT disc_id FROM tb_fixtures WHERE disc_id IS NOT NULL")
        if df_ids.empty:
            return []

        disc_ids = [r["disc_id"] for r in df_ids.to_dict(orient="records")]

        # Map disc_id to sport names
        placeholders = ",".join("?" * len(disc_ids))
        query = f"SELECT game_id, dist_game_nm FROM tb_discipline WHERE game_id IN ({placeholders})"
        df_names = ds.query(query, tuple(disc_ids))
        if df_names.empty:
            return []

        sports = sorted(set(df_names["dist_game_nm"].tolist()))
        return sports
    except Exception as e:
        print(f"Error in get_fixture_sports: {e}")
        return []


def get_disciplines_by_level(level_name):
    """
    Get list of disciplines (games) played at a specific level.
    Filtering based on `cat_no` in tb_discipline:
    - Cluster: cat_no = 4
    - Mandal: cat_no IN (3, 4)
    - Assembly: cat_no IN (3, 4, 5)
    - District: cat_no IN (2, 3, 4, 5)
    - State: cat_no IN (1, 2, 3, 4, 5)
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
        level = level_name.lower().strip()
    
        level_cat_map = {
            "cluster": [4],
            "village": [4],
            "mandal": [3, 4],
            "assembly": [3, 4, 5],
            "district": [2, 3, 4, 5],
            "state": [1, 2, 3, 4, 5]
        }
        
        allowed_cats = level_cat_map.get(level)
        if not allowed_cats:
            return []
        
        placeholders = ",".join("?" * len(allowed_cats))
        query = f"SELECT dist_game_nm FROM tb_discipline WHERE cat_no IN ({placeholders})"
        params = list(allowed_cats)
                
        df = ds.query(query, tuple(params))
        
        if df.empty:
            return []
            
        return [r['dist_game_nm'] for r in df.to_dict(orient="records")]
    except Exception as e:
        print(f"Error in get_disciplines_by_level for '{level_name}': {e}")
        return []
        

def get_player_venues_by_phone(phone):
    """
    Get venue and incharge details for a player by phone number.
    Returns list of dicts with: sport_name, venue, cluster_incharge, incharge_mobile, player_reg_id.
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
        query = """
        SELECT 
            d.dist_game_nm as sport_name,
            e.event_name,
            p.player_reg_id,
            
            -- Venue Info (from Fixtures)
            f.venue,
            f.match_date,
            
            -- Cluster Incharge Info
            c.clustername,
            c.incharge_name as cluster_incharge,
            c.mobile_no as incharge_mobile

        FROM player_details p
        
        -- Link Village -> Cluster
        LEFT JOIN villagemaster v ON p.village_id = v.id
        LEFT JOIN clustermaster c ON v.cluster_id = c.cluster_id
        
        -- Link Game/Event
        LEFT JOIN tb_discipline d ON p.game_id = d.game_id
        LEFT JOIN tb_events e ON p.event_id = e.id

        -- Link Fixtures (Try to find a match for this player's gender/district/game)
        -- Note: This is best-effort mapping since checking individual participation in a team fixture is complex.
        LEFT JOIN tb_fixtures f ON 
            p.game_id = f.disc_id 
            AND p.gender = f.gender
            AND (p.district_id = f.team1_dist_id OR p.district_id = f.team2_dist_id)

        WHERE p.mobile_no = ?
        """
        
        df = ds.query(query, (str(phone),))
        
        if df.empty:
            return []
            
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error in get_player_venues_by_phone for '{phone}': {e}")
        return []

def get_player_venue_by_ack(ack_no):
    """
    Get venue and incharge details for a player by Ack No (Reg ID).
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
        query = """
        SELECT 
            p.player_nm,
            p.player_reg_id,
            p.gender,
            d.dist_game_nm as sport_name,
            e.event_name,
            
            -- Location Hierarchy
            v.villagename,
            m.mandalname,
            dist.districtname,
            c.clustername,
            
            -- Selection Level
            sp.is_mandal_level,
            sp.is_district_level,
            sp.is_state_level,

            -- Venue & Incharge
            f.venue,
            f.match_date,
            c.incharge_name as cluster_incharge,
            c.mobile_no as incharge_mobile

        FROM player_details p
        LEFT JOIN villagemaster v ON p.village_id = v.id
        LEFT JOIN mandalmaster m ON p.mandal_id = m.id
        LEFT JOIN districtmaster dist ON p.district_id = dist.districtno
        LEFT JOIN clustermaster c ON v.cluster_id = c.cluster_id
        LEFT JOIN tb_discipline d ON p.game_id = d.game_id
        LEFT JOIN tb_events e ON p.event_id = e.id
        LEFT JOIN tb_selected_players sp ON p.id = sp.player_id
        LEFT JOIN tb_fixtures f ON 
            p.game_id = f.disc_id 
            AND p.gender = f.gender
            AND (p.district_id = f.team1_dist_id OR p.district_id = f.team2_dist_id)
        WHERE p.player_reg_id = ?
        """
        
        df = ds.query(query, (str(ack_no),))
        
        if df.empty:
            return None
            
        return df.to_dict(orient="records")[0]
    except Exception as e:
        print(f"Error in get_player_venue_by_ack for '{ack_no}': {e}")
        return None


def get_discipline_info(sport_name):
    """
    Get basic info including ID for a sport from tb_discipline.
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
        query = "SELECT game_id, dist_game_nm, rules_pdf FROM tb_discipline WHERE LOWER(dist_game_nm) LIKE ?"
        df = ds.query(query, (sport_name.lower(),))
        
        if df.empty:
            df = ds.query(query, (f"%{sport_name.lower()}%",))
            
        if df.empty:
            return None
            
        return df.to_dict(orient="records")[0]
    except Exception as e:
        print(f"Error in get_discipline_info for '{sport_name}': {e}")
        return None

def get_categories_by_sport(game_id):
    """
    Get age criteria/categories for a sport ID from tb_category.
    """
    try:
        ds = get_datastore()
        if not ds.initialized: 
            ds.init_db()
    
        query = """
        SELECT 
            c.cat_name, 
            c.gender, 
            c.from_age, 
            c.to_age 
        FROM tb_category c 
        WHERE c.discipline_id = ? AND c.status = 1
        """
        
        df = ds.query(query, (game_id,))
        
        if df.empty:
            return []
            
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error in get_categories_by_sport for game_id '{game_id}': {e}")
        return []

def get_sport_rules(sport_name):
    """
    Derived rule info from discipline and categories.
    """
    info = get_discipline_info(sport_name)
    if not info:
        return None
    
    game_id = info['game_id']
    cats = get_categories_by_sport(game_id)
    
    min_age = 99
    max_age = 0
    if cats:
        for c in cats:
            try:
                min_age = min(min_age, int(c.get('from_age', 99)))
                max_age = max(max_age, int(c.get('to_age', 0)))
            except:
                pass
                
    if min_age == 99: min_age = "N/A"
    if max_age == 0: max_age = "N/A"

    return {
        "sport_name": info['dist_game_nm'],
        "min_age": min_age,
        "max_age": max_age,
        "team_size": "Details in Rules PDF",
        "is_para": '0'
    }

def extract_district_from_query(user_query):
    """
    Extracts a valid district name from a natural language query.
    """
    ds = get_datastore()
    if not ds.initialized: ds.init_db()
    
    # Get all valid districts
    df = ds.query("SELECT districtname FROM districtmaster")
    if df.empty:
        return None
        
    valid_districts = [d.lower() for d in df['districtname'].tolist()]
    
    # Normalize query
    query_lower = user_query.lower()
    
    # Find matches - Prioritize longest match to avoid substring issues (e.g. 'Warangal' vs 'Warangal Urban' if exists)
    # Sort districts by length descending
    valid_districts.sort(key=len, reverse=True)
    
    for dist in valid_districts:
        # Check exact word match or if it's part of the string
        # Using word boundary check is safer but simple substring is often enough for unique names
        if dist in query_lower:
            return dist # Return the first (longest) match found
            
    return None
