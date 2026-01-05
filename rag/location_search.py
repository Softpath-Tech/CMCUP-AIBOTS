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
    Search for Cluster In-charge details.
    Priority 1: DistrictWIseClusters.xlsx (New Data)
    Priority 2: Mandal_Incharges_Cleaned.txt (Old Data - Fallback)
    """
    query_str = query_name.strip().lower()

    try:
        # --- PRIORITY 1: EXCEL LOOKUP ---
        file_path = "data/new data/DistrictWIseClusters.xlsx"
        
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            
            # Clean Cluster Names
            df['ClusterName_clean'] = df['Cluster Name'].astype(str).str.strip().str.lower()
            
            # 1a. Exact Match
            match = df[df['ClusterName_clean'] == query_str]
            
            # 1b. Fuzzy Match
            if match.empty:
                import difflib
                all_clusters = df['ClusterName_clean'].unique().tolist()
                matches = difflib.get_close_matches(query_str, all_clusters, n=1, cutoff=0.6)
                if matches:
                    match = df[df['ClusterName_clean'] == matches[0]]

            if not match.empty:
                rec = match.iloc[0]
                return {
                    "type": "Cluster",
                    "data": {
                        "clustername": rec['Cluster Name'],
                        "incharge_name": rec['Incharge Name'],
                        "mobile_no": str(rec['Mobile No']),
                        "district_name": rec['District Name'],
                        "mandal_name": rec['Mandal Name'],
                        "source": "DistrictWIseClusters.xlsx"
                    }
                }

        # --- PRIORITY 2: TEXT FILE FALLBACK ---
        # If not found in Excel, try the old text file
        txt_path = "data/new data/Mandal_Incharges_Cleaned.txt"
        if os.path.exists(txt_path):
            import difflib
            
            results = []
            cluster_map = {} # {cluster_lower: [line1, line2]}
            
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "Cluster:" in line:
                        # Parse: Mandal: ... | Cluster: XYZ | ...
                        parts = line.split("|")
                        if len(parts) >= 2:
                            # Extract " Cluster: XYZ " -> "XYZ"
                            try:
                                c_raw = parts[1].split(":")[1].strip()
                                c_lower = c_raw.lower()
                                
                                if c_lower not in cluster_map:
                                    cluster_map[c_lower] = []
                                cluster_map[c_lower].append(line.strip())
                            except:
                                continue

            # 2a. Exact Match
            if query_str in cluster_map:
                results = cluster_map[query_str]
                found_name = query_str
            else:
                # 2b. Fuzzy Match
                all_txt_clusters = list(cluster_map.keys())
                matches = difflib.get_close_matches(query_str, all_txt_clusters, n=1, cutoff=0.6)
                if matches:
                    found_name = matches[0]
                    results = cluster_map[found_name]
            
            if results:
                # Parse the first result line to structure it roughly
                # Line format: Mandal: X | Cluster: Y | Incharge Details: Z | Contact: 123
                first_line = results[0]
                parts = first_line.split("|")
                
                # Safe extraction helper
                def maximize_val(p_list, key):
                    for p in p_list:
                        if key in p: return p.split(":")[1].strip()
                    return "N/A"

                mandal = maximize_val(parts, "Mandal")
                cluster = maximize_val(parts, "Cluster")
                incharge = maximize_val(parts, "Incharge Details")
                contact = maximize_val(parts, "Contact")

                return {
                    "type": "Cluster (Fallback)",
                    "data": {
                        "clustername": cluster,
                        "incharge_name": incharge,
                        "mobile_no": contact,
                        "district_name": "Unknown (Fallback)",
                        "mandal_name": mandal,
                        "source": "Mandal_Incharges_Cleaned.txt"
                    }
                }

        return None


    except Exception as e:
        print(f"Error in search_cluster_incharge: {e}")
        return None

def search_mandal_incharge(mandal_name):
    """
    Search for Mandal In-charge (MEO) details from MEO_Details.xlsx
    """
    try:
        file_path = "data/new data/MEO_Details.xlsx"
        if not os.path.exists(file_path):
            return None
            
        df = pd.read_excel(file_path)
        
        # Clean for matching
        # BLKNAME seems to be the Mandal Name based on inspection
        df['Mandal_clean'] = df['BLKNAME'].astype(str).str.strip().str.lower()
        query_str = mandal_name.strip().lower()
        
        # 1. Exact Match
        match = df[df['Mandal_clean'] == query_str]
        
        # 2. Fuzzy Match
        if match.empty:
            import difflib
            all_mandals = df['Mandal_clean'].unique().tolist()
            matches = difflib.get_close_matches(query_str, all_mandals, n=1, cutoff=0.6)
            if matches:
                 match = df[df['Mandal_clean'] == matches[0]]
        
        if not match.empty:
            rec = match.iloc[0]
            return {
                "mandal_name": rec['BLKNAME'],
                "incharge_name": rec['EmployeeName'],
                "mobile_no": str(rec['mobile']),
                "district_name": rec['DISTNAME'],
                "designation": "Mandal Educational Officer (MEO)"
            }
            
        return None

    except Exception as e:
        print(f"Error in search_mandal_incharge: {e}")
        return None

