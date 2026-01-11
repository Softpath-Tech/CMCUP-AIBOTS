import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.sql_queries import get_disciplines_by_level

def test_levels():
    mandal_games = get_disciplines_by_level("mandal")
    district_games = get_disciplines_by_level("district")
    
    print(f"Mandal Games ({len(mandal_games)}): {mandal_games[:5]}...")
    print(f"District Games ({len(district_games)}): {district_games[:5]}...")
    
    if mandal_games == district_games:
        print("❌ CRITICAL: Mandal and District lists are IDENTICAL!")
    else:
        print("✅ Mandal and District lists are different.")
        
    # Check intersection
    common = set(mandal_games).intersection(set(district_games))
    print(f"Common Games: {len(common)}")
    
    # Check exclusive to District
    dist_only = set(district_games) - set(mandal_games)
    print(f"District Only Games: {dist_only}")

if __name__ == "__main__":
    test_levels()
