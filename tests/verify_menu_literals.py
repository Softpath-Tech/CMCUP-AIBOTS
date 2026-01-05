
import sys
import os
import asyncio

# Mock project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import get_menu_text

def verify_literals():
    print("=== TEST: Menu Literals Verification ===\n")
    
    # Test District
    print("🔹 Testing 'MENU_OFFICERS_DISTRICT'...")
    txt1 = get_menu_text("MENU_OFFICERS_DISTRICT")
    print(f"   Result: {txt1[:50]}...")
    if "District Sports Officers" in txt1:
        print("   ✅ SUCCESS")
    else:
        print("   ❌ FAILED")

    # Test Cluster
    print("\n🔹 Testing 'MENU_OFFICERS_CLUSTER'...")
    txt2 = get_menu_text("MENU_OFFICERS_CLUSTER")
    print(f"   Result: {txt2[:50]}...")
    if "Venue In-Charge" in txt2:
        print("   ✅ SUCCESS")
    else:
        print("   ❌ FAILED")

if __name__ == "__main__":
    verify_literals()
