
import sys
import os
import asyncio
import pandas as pd

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.location_search import search_district_officer, search_cluster_incharge

def verify_mapping():
    print("=== TEST: Data Mapping Verification ===\n")

    # 1. District Officer Search
    # We saw 'Adilabad' in tb_district_officers.csv
    dist_query = "Adilabad"
    print(f"🔹 Testing District Search: '{dist_query}'")
    officer = search_district_officer(dist_query)
    
    if officer:
        print(f"   ✅ FOUND: {officer.get('district_name')} - {officer.get('special_officer_name')}")
    else:
        print(f"   ❌ FAILED: Could not find '{dist_query}'")

    # 2. Cluster In-Charge Search
    # We saw 'ADILABAD' in clustermaster.csv
    cluster_query = "ADILABAD"
    print(f"\n🔹 Testing Cluster Search: '{cluster_query}'")
    res = search_cluster_incharge(cluster_query)
    
    if res:
        print(f"   ✅ FOUND: {res.get('type')} - {res['data'].get('clustername')}")
        print(f"   Details: Name={res['data'].get('incharge_name')}, Mobile={res['data'].get('mobile_no')}")
    else:
        print(f"   ❌ FAILED: Could not find '{cluster_query}'")

if __name__ == "__main__":
    verify_mapping()
