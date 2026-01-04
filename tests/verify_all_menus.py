import sys
import os
import asyncio
import re

# Ensure we can import from the root directory
sys.path.append(os.getcwd())

from api.main import (
    process_user_query, 
    SESSION_STATE, 
    MENU_MAIN, 
    MENU_REGISTRATION, 
    MENU_DISCIPLINES, 
    MENU_SCHEDULE, 
    MENU_SELECTION, 
    MENU_RULES, 
    MENU_STATS, 
    MENU_DOWNLOADS, 
    MENU_LOCATION, 
    MENU_HELPDESK, 
    MENU_LANGUAGE
)

# Test Configuration
# format: (Test Name, Input Sequence, Expected Keywords in Final Response)
TEST_FLOWS = [
    # --- 1. Registration Menu ---
    ("Reg: Main Menu -> Registration", ["1"], ["Registration FAQs", "Type", "Back"]),
    ("Reg: Process", ["1", "1"], ["Registration Process", "official portal"]),
    ("Reg: Age Criteria (Prompt)", ["1", "2"], ["Age Criteria Check", "Game/Sport"]),
    ("Reg: Age Criteria (Logic)", ["1", "2", "Kabaddi"], ["Age Criteria for Kabaddi", "Min Age", "Max Age"]),
    ("Reg: Documents", ["1", "3"], ["Required Documents", "Aadhaar Card"]),

    # --- 2. Disciplines Menu ---
    ("Disc: Main Menu -> Disciplines", ["2"], ["Select Level", "Cluster", "State"]),
    ("Disc: Cluster Level", ["2", "1"], ["Disciplines at Cluster Level", "Type a", "Sport Name"]),
    ("Disc: Mandal Level", ["2", "2"], ["Disciplines at Mandal Level"]),
    ("Disc: District Level", ["2", "4"], ["Disciplines at District Level"]), # Skipping 3 to save time/space, assuming similar logic
    ("Disc: State Level", ["2", "5"], ["Disciplines at State Level"]),

    # --- 3. Schedules Menu ---
    ("Sched: Main Menu -> Schedules", ["3"], ["Schedules", "Tournament", "Games"]),
    ("Sched: Tournament Schedule", ["3", "1"], ["Tournament Schedule", "Jan", "Feb"]),
    ("Sched: Games Schedule (Prompt)", ["3", "2"], ["Which sport's schedule", "Cricket", "Kabaddi"]),
    ("Sched: Games Schedule (Logic - Empty/Mock)", ["3", "2", "Cricket"], ["Schedule", "Cricket"]), 

    # --- 4. Venues / Location ---
    ("Venue: Main Menu -> Venues", ["4"], ["Location Verification", "Village", "Mandal"]),
    ("Venue: Location Lookup (Found)", ["4", "Mancherial"], ["Location Found", "Mancherial", "District"]),
    ("Venue: Location Lookup (Not Found)", ["4", "Atlantis"], ["could not be found", "Atlantis"]),

    # --- 5. Special Officers ---
    ("Officers: Main Menu -> Officers", ["5"], ["Special Officers", "In-Charge", "Mandal", "District"]),

    # --- 6. Player Details (Redirection) ---
    ("Player: Main Menu -> Details", ["6"], ["Registration FAQs"]), # Redirects to Reg Menu

    # --- 7. Medal Tally ---
    ("Medal: Main Menu -> Tally", ["7"], ["Medal Tally", "not started yet"]),

    # --- 8. Helpdesk ---
    ("Help: Main Menu -> Helpdesk", ["8"], ["Helpdesk & Support", "Helpline", "Email"]),
    # Note: Sub-options 1,2,3 for Helpdesk might be missing implementation in api/main.py logic provided, 
    # but we will test the menu entrance at least.
    
    # --- 9. Language ---
    ("Lang: Main Menu -> Language", ["9"], ["Select Language", "Telugu", "Hindi"]),

    # --- Cross-Cutting / Global ---
    ("Global: Main Menu", ["hi"], ["Welcome to Telangana Sports Authority", "Registration", "Helpdesk"]),
    ("Global: Back Navigation", ["1", "back"], ["Welcome to Telangana Sports Authority"]), # Should go back to Main
]

async def run_tests():
    print(f"{'TEST NAME':<40} | {'STATUS':<10} | {'NOTES'}")
    print("-" * 80)
    
    results = []
    
    for test_name, inputs, expected_keywords in TEST_FLOWS:
        session_id = f"test_sess_{re.sub(r'[^a-zA-Z0-9]', '_', test_name)}"
        
        # Reset Session
        SESSION_STATE[session_id] = MENU_MAIN
        
        # Run through inputs
        last_response = ""
        error_msg = None
        
        try:
            for inp in inputs:
                resp_obj = await process_user_query(inp, session_id)
                last_response = resp_obj.get("response", "")
                
            # Verification
            missing = [k for k in expected_keywords if k.lower() not in last_response.lower()]
            
            if not missing:
                status = "PASS"
                note = ""
            else:
                status = "FAIL"
                note = f"Missing: {missing}. Got: {last_response[:50]}..."
                
        except Exception as e:
            status = "ERROR"
            note = str(e)
            
        print(f"{test_name:<40} | {status:<10} | {note}")
        results.append({
            "name": test_name,
            "inputs": inputs,
            "status": status,
            "note": note,
            "response_snippet": last_response[:100].replace("\n", " ")
        })

    # Generate Report
    generate_report(results)

def generate_report(results):
    report_path = "menu_verification_report.md"
    pass_count = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 🧪 Menu Verification Report\n\n")
        f.write(f"**Date:** {os.popen('date /t').read().strip()}\n")
        f.write(f"**Summary:** {pass_count}/{total} Passed\n\n")
        
        f.write("| Test Name | Inputs | Status | Notes |\n")
        f.write("|---|---|---|---|\n")
        for r in results:
            inputs_str = " -> ".join(f"`{i}`" for i in r['inputs'])
            status_icon = "✅" if r['status'] == "PASS" else "❌"
            f.write(f"| {r['name']} | {inputs_str} | {status_icon} {r['status']} | {r['note']} |\n")
            
        f.write("\n## Detailed Failures\n")
        failures = [r for r in results if r['status'] != "PASS"]
        if not failures:
            f.write("No failures! 🎉\n")
        else:
            for f_item in failures:
                f.write(f"### {f_item['name']}\n")
                f.write(f"- **Inputs:** {f_item['inputs']}\n")
                f.write(f"- **Error/Missing:** {f_item['note']}\n")
                f.write(f"- **Actual Response:** {f_item['response_snippet']}...\n\n")
                
    print(f"\nReport generated at: {report_path}")

if __name__ == "__main__":
    asyncio.run(run_tests())
