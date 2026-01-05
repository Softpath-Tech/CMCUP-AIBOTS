
import sys
import os
import difflib

# Mock the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import (
    get_menu_text, 
    MENU_OFFICERS, 
    MENU_OFFICERS_DISTRICT, 
    MENU_OFFICERS_CLUSTER,
    STATE_WAIT_DIST_OFFICER, 
    STATE_WAIT_CLUSTER_INCHARGE
)
from rag.location_search import search_district_officer, search_cluster_incharge

def test_menu_text():
    print("\n--- Testing Menu Text ---")
    print(f"OFFICERS MENU:\n{get_menu_text(MENU_OFFICERS)}")
    print(f"OFFICERS DISTRICT:\n{get_menu_text(MENU_OFFICERS_DISTRICT)}")
    print(f"OFFICERS CLUSTER:\n{get_menu_text(MENU_OFFICERS_CLUSTER)}")

def test_district_officer_search():
    print("\n--- Testing District Officer Search ---")
    # Test with seed data known to be in tb_district_officers.csv (e.g., 'Warangal')
    res = search_district_officer("Warangal")
    if res:
        print(f"✅ Found Warangal Officer: {res}")
    else:
        print("❌ Failed to find Warangal Officer")
        
    res_fake = search_district_officer("FakeDistrict")
    if not res_fake:
        print("✅ Correctly returned None for FakeDistrict")
    else:
        print(f"❌ Incorrectly found data for FakeDistrict: {res_fake}")

def test_cluster_search():
    print("\n--- Testing Cluster Search ---")
    # Using 'CHANDA' which is seen in clustermaster.csv
    res = search_cluster_incharge("CHANDA")
    if res and res.get('type') == 'Cluster':
        print(f"✅ Found Cluster: {res}")
    else:
        print("❌ Failed to find Akinepalli Cluster")

    # Test Village Mapping (Need a valid village-cluster pair)
    # Assuming 'Allikori' maps to something if it exists, or let's try a known village.
    # I'll just try 'Akinepalli' again as a village search test if the mock allows, 
    # but strictly I should pick a village. I'll rely on what I saw in files earlier.
    # villagemaster -> cluster_id -> clustermaster
    
    res_fake = search_cluster_incharge("NonExistentPlace")
    if not res_fake:
        print("✅ Correctly returned None for NonExistentPlace")

if __name__ == "__main__":
    test_menu_text()
    test_district_officer_search()
    test_cluster_search()
