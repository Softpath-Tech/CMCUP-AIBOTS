from rag.data_store import get_datastore
import pandas as pd

def search_district_officer(district_name):
    """
    Search for Special Officers by District Name in tb_district_officers.
    """
    ds = get_datastore()
    if not ds.initialized:
        ds.init_db()
        
    # clean input
    query_dist = district_name.strip().lower()
    
    # query
    sql = """
    SELECT district_name, special_officer_name, contact_no, designation
    FROM tb_district_officers
    WHERE LOWER(district_name) LIKE ?
    """
    
    df = ds.query(sql, (f"%{query_dist}%",))
    
    if df.empty:
        return None
        
    return df.to_dict(orient="records")[0]

def search_cluster_incharge(query_name):
    """
    Search for Cluster In-charge details.
    Logic:
    1. Try to find the input as a Cluster Name.
    2. If not found, try to find the input as a Village Name, map to Cluster, then find Cluster.
    """
    ds = get_datastore()
    if not ds.initialized:
        ds.init_db()
        
    q_str = query_name.strip().lower()
    
    # 1. Direct Cluster Search
    sql_cluster = """
    SELECT clustername, incharge_name, mobile_no
    FROM clustermaster
    WHERE LOWER(clustername) LIKE ?
    """
    df_cluster = ds.query(sql_cluster, (f"%{q_str}%",))
    
    if not df_cluster.empty:
        return {
            "type": "Cluster",
            "data": df_cluster.to_dict(orient="records")[0]
        }
        
    # 2. Village Mapping Search
    # Find village, get cluster_id, then get cluster info
    sql_village = """
    SELECT v.villagename, c.clustername, c.incharge_name, c.mobile_no
    FROM villagemaster v
    JOIN clustermaster c ON v.cluster_id = c.cluster_id
    WHERE LOWER(v.villagename) LIKE ?
    """
    df_village = ds.query(sql_village, (f"%{q_str}%",))
    
    if not df_village.empty:
        return {
            "type": "Village",
            "mapped_cluster": df_village.iloc[0]['clustername'],
            "data": df_village.to_dict(orient="records")[0]
        }
        
    return None
