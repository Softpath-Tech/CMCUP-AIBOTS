from rag.data_store import get_datastore
import pandas as pd
import os

def search_district_officer(district_name):
    """
    Search for Special Officers by District Name using district_officers.csv.
    """
    try:
        # Load Data
        users_path = "data/new data/district_officers.csv"
        
        if not os.path.exists(users_path):
             return None
             
        df_users = pd.read_csv(users_path)
        
        # Clean District Names for matching
        # The new CSV has 'DistrictName' column directly
        df_users['DistrictName_clean'] = df_users['DistrictName'].astype(str).str.strip().str.lower()
        query_dist = district_name.strip().lower()
        
        # Find District Match
        dist_match = df_users[df_users['DistrictName_clean'] == query_dist]
        
        if dist_match.empty:
            # Try fuzzy match if exact match fails
            import difflib
            all_dists = df_users['DistrictName_clean'].unique().tolist()
            matches = difflib.get_close_matches(query_dist, all_dists, n=1, cutoff=0.7)
            if matches:
                 dist_match = df_users[df_users['DistrictName_clean'] == matches[0]]
            else:
                return None
        
        # Get the first matching record (assuming one officer per district in this file or taking the first one)
        rec = dist_match.iloc[0]
        
        return {
            "district_name": rec['DistrictName'],
            "special_officer_name": rec['name'],
            "contact_no": str(rec['dyso_cont_no']),
            "designation": rec['dyso_dept'] 
        }

    except Exception as e:
        print(f"Error in search_district_officer: {e}")
        return None

def search_cluster_incharge(query_name):
    """
    Search for Cluster In-charge details using DistrictWIseClusters.xlsx
    """
    try:
        # Load Data
        file_path = "data/new data/DistrictWIseClusters.xlsx"
        
        if not os.path.exists(file_path):
             return None
             
        df = pd.read_excel(file_path)
        
        # Clean Cluster Names for matching
        # Data columns: ['Sl.No', 'District Name', 'Mandal Name', 'Cluster Name', 'Incharge Name', 'Mobile No']
        df['ClusterName_clean'] = df['Cluster Name'].astype(str).str.strip().str.lower()
        query_str = query_name.strip().lower()
        
        # 1. Exact Match
        match = df[df['ClusterName_clean'] == query_str]
        
        if match.empty:
            # 2. Fuzzy Match
            import difflib
            all_clusters = df['ClusterName_clean'].unique().tolist()
            # Try close matches
            matches = difflib.get_close_matches(query_str, all_clusters, n=1, cutoff=0.6)
            
            if matches:
                match = df[df['ClusterName_clean'] == matches[0]]
            else:
                return None

        # Get first result
        rec = match.iloc[0]
        
        return {
            "type": "Cluster",
            "data": {
                "clustername": rec['Cluster Name'],
                "incharge_name": rec['Incharge Name'],
                "mobile_no": str(rec['Mobile No']),
                "district_name": rec['District Name'],
                "mandal_name": rec['Mandal Name']
            }
        }

    except Exception as e:
        print(f"Error in search_cluster_incharge: {e}")
        return None
