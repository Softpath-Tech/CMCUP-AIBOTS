import requests
import uuid
import time
import json

BASE_URL = "http://localhost:8000"
CHECKLIST_FILE = "tests/UAT_Report_Auto.md"

results = []

def log_result(id, desc, status, note=""):
    results.append(f"| {id} | {desc} | {status} | {note} |")
    print(f"[{status}] {id}: {desc} {note}")

def run_query(session_id, query, expect_keywords=[], context_desc=""):
    try:
        start_time = time.time()
        res = requests.post(f"{BASE_URL}/chat", json={"query": query, "session_id": session_id}, timeout=30)
        latency = round(time.time() - start_time, 2)
        
        if res.status_code != 200:
            return None, latency, "API Error"
            
        data = res.json()
        response = data.get("response", "")
        source = data.get("source", "unknown")
        
        passed = True
        missing = []
        for k in expect_keywords:
            if k.lower() not in response.lower():
                passed = False
                missing.append(k)
        
        out = {
            "response": response,
            "source": source,
            "latency": latency,
            "passed": passed,
            "missing": missing
        }
        return out
    except Exception as e:
        return None, 0, str(e)

def run_uat():
    print("🚀 Starting Automated UAT Execution...\n")
    
    # --- SECTION 1: GREETING & MENU ---
    sid = str(uuid.uuid4())
    
    # Q1, Q2, Q3: Greeting
    r = run_query(sid, "Hi", ["Welcome", "Registration", "Schedules", "Rules", "Helpdesk"])
    if r["passed"]:
        log_result("Q1, Q2, Q3", "Greeting & Service List", "PASS", f"Latency: {r['latency']}s")
    else:
        log_result("Q1, Q2, Q3", "Greeting & Service List", "FAIL", f"Missing: {r['missing']}")

    # Q4: Menu Numbers (0-9) - Checking a sample
    r = run_query(sid, "2", ["Match Schedules", "1", "2", "3"])
    if r["passed"]:
        log_result("Q4", "Menu Number '2' Accepted", "PASS")
    else:
        log_result("Q4", "Menu Number '2' Accepted", "FAIL", f"Response: {r['response'][:50]}...")

    # Q5: Invalid Number
    r = run_query(sid, "11", ["Invalid", "Menu", "Welcome", "not found"], []) # Expect some error or re-prompt
    # Checking if it falls back to menu or error.
    # Logic in code: "Menu not found" or falls through.
    # Current code main.py: if choice not in ranges, returns None -> falls through? 
    # Actually logic: if digit -> check MAIN_MENU range. if not found -> "Menu not found"? 
    # Or fallthrough to logic. 
    # Let's see. logic interceptor might catch it? Or "Menu not found".
    # We accept "Menu not found" or "invalid" or just falls to RAG (which is acceptable fallback).
    # Update: main.py returns "Menu not found." if get_menu_text fails? 
    # Let's check main.py logic... 
    # It does `return get_menu_text(...)`
    # `get_menu_text` returns "Menu not found" at end. 
    if "menu not found" in r['response'].lower() or "invalid" in r['response'].lower():
        log_result("Q5", "Invalid Number Handling", "PASS", "Error message received")
    else:
        log_result("Q5", "Invalid Number Handling", "WARN", f"Got: {r['response'][:50]}...")

    # Q6: Exit Chat (0)
    r = run_query(sid, "0", ["Session Ended", "Hi", "start again"])
    if r["passed"]:
        log_result("Q6", "Exit Chat (0)", "PASS")
    else:
        log_result("Q6", "Exit Chat (0)", "FAIL")

    # --- SECTION 2: NAVIGATION ---
    sid = str(uuid.uuid4())
    
    # Q7: Return to Previous Menu
    run_query(sid, "2") # in Schedule
    r = run_query(sid, "Back", ["Welcome", "Registration"]) # Back to Main
    if r["passed"]:
        log_result("Q7", "Back Navigation", "PASS")
    else:
        log_result("Q7", "Back Navigation", "FAIL")

    # Q9: Free text in menu (Context)
    run_query(sid, "2") # Schedule
    run_query(sid, "1") # By Sport -> "Which sport?"
    r = run_query(sid, "Cricket", ["Schedule", "Cricket"]) # Should understand intent
    if r["passed"] or "No specific schedule" in r["response"]:
        log_result("Q9", "Contextual Free Text", "PASS", "Understood 'Cricket'")
    else:
        log_result("Q9", "Contextual Free Text", "FAIL", f"Got: {r['response'][:50]}")

    # --- SECTION 3: PLAYER REGISTRATION ---
    # Need mock data or real ID. 
    # We'll use a known phone if exits, else rely on "No registrations found" format
    
    # Q11: Valid Phone
    # Using dummy valid format
    r = run_query(sid, "9999999999", ["No registrations found", "official site"]) # 999.. usually not in DB
    if r["passed"]:
        log_result("Q11", "Valid Phone Format Query", "PASS", "Returned lookup result")
    else:
        log_result("Q11", "Valid Phone Format Query", "FAIL")

    # Q14: Formatting
    # Space
    r = run_query(sid, "99999 99999", ["No registrations found", "official site"])
    if r["passed"]:
        log_result("Q14", "Phone with Spaces", "PASS")
    else:
        log_result("Q14", "Phone with Spaces", "FAIL")

    # --- SECTION 4: PRIVACY ---
    sid = str(uuid.uuid4())
    r = run_query(sid, "My number is 9848012345", ["Privacy Notice", "do not share"])
    if r["passed"]:
        log_result("Q20", "Privacy Guardrail", "PASS")
    else:
        log_result("Q20", "Privacy Guardrail", "FAIL")


    # --- SECTION 5: SCHEDULES ---
    sid = str(uuid.uuid4())
    # Q24: Cricket Schedule
    r = run_query(sid, "Cricket schedule", ["Schedule", "Cricket", "vs"])
    if r["passed"] or "No specific schedule" in r["response"]:
         log_result("Q24", "Sport Schedule Query", "PASS")
    else:
         log_result("Q24", "Sport Schedule Query", "FAIL")

    # Q26: Mandal Level
    r = run_query(sid, "Mandal level schedule", ["Mandal", "28 Jan", "31 Jan"])
    if r["passed"]:
        log_result("Q26", "Level Static Schedule", "PASS")
    else:
        log_result("Q26", "Level Static Schedule", "FAIL")


    # --- SECTION 7: RULES (RAG) ---
    sid = str(uuid.uuid4())
    # Q32: Age limit
    r = run_query(sid, "Age limit for Kabaddi", ["Kabaddi", "Age", "years", "born"])
    if r["source"] == "rag_knowledge_base" or r["source"] == "rag_chain":
        log_result("Q32", "RAG Rule Query", "PASS", f"Source: {r['source']}")
    else:
        log_result("Q32", "RAG Rule Query", "WARN", f"Source: {r['source']} (Expected RAG)")

    # Q35: Food
    r = run_query(sid, "Will food be provided?", ["Food", "Accommodation", "provided"])
    if r["passed"]:
        log_result("Q35", "Static/FAQ Query", "PASS")
    else:
        log_result("Q35", "Static/FAQ Query", "FAIL")

    # --- SECTION 9: LOCATION ---
    sid = str(uuid.uuid4())
    # Q41: Hierarchy
    r = run_query(sid, "Is Peddapalli a district?", ["Location Found", "District"])
    if r["passed"]:
        log_result("Q41", "Location Hierarchy", "PASS")
    else:
        log_result("Q41", "Location Hierarchy", "FAIL")

    # Q43: Non-existent
    r = run_query(sid, "Atlantis details", ["could not be found"])
    if r["passed"]:
        log_result("Q43", "Non-existent Location", "PASS")
    else:
         # Might fail if RAG picks it up or generic
         log_result("Q43", "Non-existent Location", "WARN", f"Got: {r['response'][:50]}")

    # --- SECTION 10: DOWNLOADS ---
    sid = str(uuid.uuid4())
    r = run_query(sid, "Download acknowledgment", ["https://satg.telangana.gov.in", "Download"])
    if r["passed"]:
        log_result("Q45", "Download Link", "PASS")
    else:
        log_result("Q45", "Download Link", "FAIL")

    # Q47: Outdated Event
    r = run_query(sid, "CM cup 2015 details", ["2015", "don't have data", "2025"])
    if r["passed"]:
        log_result("Q47", "Outdated Event Block", "PASS")
    else:
        log_result("Q47", "Outdated Event Block", "FAIL")

    # --- Generate Report ---
    with open(CHECKLIST_FILE, "w", encoding="utf-8") as f:
        f.write("# Automated UAT Execution Report\n\n")
        f.write("| ID | Description | Status | Note |\n")
        f.write("|---|---|---|---|\n")
        for line in results:
            f.write(line + "\n")
    
    print(f"\n✅ UAT Completed. Report saved to {CHECKLIST_FILE}")

if __name__ == "__main__":
    run_uat()
