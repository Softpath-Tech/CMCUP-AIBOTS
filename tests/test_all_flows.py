import sys
import os
import asyncio
import uuid
import json
from datetime import datetime

# Setup path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from api.main import process_user_query, SESSION_STATE, SESSION_DATA

# TEST CONFIGURATION
LANGUAGES = ["en", "te", "hi"]
LANG_NAMES = {"en": "English", "te": "Telugu", "hi": "Hindi"}

# Mock Data for Inputs
MOCK_INPUTS = {
    "district": "Warangal", 
    "mandal": "Jainad",
    "cluster": "Akinepalli",
    "phone": "9876543210",
    "ack": "SATGCMC-TEST",
    "sport": "Cricket",
    "location": "Warangal"
}

# Define Test Flows (Sequence of inputs)
TEST_FLOWS = [
    # --- 1. Registration ---
    {"name": "Reg - How to", "inputs": ["1", "1.1"]},
    {"name": "Reg - Rules", "inputs": ["1", "1.2"]},
    {"name": "Reg - Docs", "inputs": ["1", "1.3"]},
    {"name": "Reg - Status Info", "inputs": ["1", "1.4"]},
    {"name": "Reg - FAQs", "inputs": ["1", "1.5"]},
    
    # --- 2. Sports ---
    {"name": "Sports - Disciplines L1", "inputs": ["2", "2.1", "LEVEL_1"]},
    {"name": "Sports - Disciplines L4", "inputs": ["2", "2.1", "LEVEL_4"]},
    {"name": "Sports - Schedule Main", "inputs": ["2", "2.2", "2.2.1"]},
    {"name": "Sports - Game Schedule", "inputs": ["2", "2.2", "2.2.2", MOCK_INPUTS['sport']]},
    {"name": "Sports - Medals", "inputs": ["2", "2.3"]},
    
    # --- 3. Venues & Officers ---
    {"name": "Venues - List", "inputs": ["3", "3.1"]},
    {"name": "Venues - District Officer", "inputs": ["3", "3.2", MOCK_INPUTS['district']]},
    {"name": "Venues - Cluster Incharge", "inputs": ["3", "3.3", MOCK_INPUTS['cluster']]},
    {"name": "Venues - Mandal Incharge", "inputs": ["3", "3.4", MOCK_INPUTS['mandal']]},
    
    # --- 4. Player Status ---
    {"name": "Player - By Phone", "inputs": ["4", "1", MOCK_INPUTS['phone']]},
    {"name": "Player - By Ack", "inputs": ["4", "2", MOCK_INPUTS['ack']]},
    
    # --- 5. Help ---
    {"name": "Help - Helpline", "inputs": ["5", "5.1"]},
    {"name": "Help - Email", "inputs": ["5", "5.2"]},
]

REPORT_FILE = "test_run_report.md"

async def run_test_flow(flow, lang):
    sid = str(uuid.uuid4())
    SESSION_DATA[sid] = {"language": lang} # Pre-set language
    
    flow_name = flow["name"]
    inputs = flow["inputs"]
    
    results = []
    status = "PASS"
    error_msg = ""
    
    print(f"  👉 Running {flow_name} [{lang}]...")
    
    try:
        # Initial 'hi' to bootstrap if needed, but we hijack session
        # await process_user_query("hi", sid) 
        
        for i, inp in enumerate(inputs):
            resp = await process_user_query(inp, sid)
            
            # Basic Validation
            if not resp:
                status = "FAIL"
                error_msg = f"No response for input '{inp}'"
                break
            
            # Check for errors in text
            txt = resp.get("text", "")
            if "Error" in txt or "Exception" in txt:
                # Allow "Error looking up" if it's just not found vs crash
                if "valid" not in txt.lower() and "found" not in txt.lower():
                     status = "WARNING" 
                     error_msg = f"Potential error msg: {txt[:50]}..."

            results.append({
                "input": inp,
                "response_text": txt[:100].replace("\n", " ") + "...",
                "menus_count": len(resp.get("menus", []))
            })
            
    except Exception as e:
        status = "ERROR"
        error_msg = str(e)
        
    return {
        "flow": flow_name,
        "lang": lang,
        "status": status,
        "error": error_msg,
        "steps": results
    }

async def main():
    print(f"🚀 Starting Comprehensive Test Run at {datetime.now()}")
    
    all_results = []
    
    for lang in LANGUAGES:
        print(f"\n🌍 TESTING LANGUAGE: {LANG_NAMES[lang]} ({lang})")
        for flow in TEST_FLOWS:
            res = await run_test_flow(flow, lang)
            all_results.append(res)
            
    # GENERATE REPORT
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 🕵️ Chatbot Comprehensive Test Report\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary Table
        f.write("## 📊 Summary\n\n")
        f.write("| Flow Name | Language | Status | Notes |\n")
        f.write("|---|---|---|---|\n")
        
        for r in all_results:
            icon = "✅" if r['status'] == "PASS" else ("⚠️" if r['status'] == "WARNING" else "❌")
            f.write(f"| {r['flow']} | {r['lang']} | {icon} {r['status']} | {r['error']} |\n")
            
        # Detailed Logs
        f.write("\n## 📝 Detailed Logs\n")
        for r in all_results:
            if r['status'] != "PASS":
                f.write(f"\n### {r['flow']} ({r['lang']})\n")
                f.write(f"**Status:** {r['status']}\n")
                if r['error']: f.write(f"**Error:** {r['error']}\n")
                f.write("**Steps:**\n")
                for s in r['steps']:
                     f.write(f"- Input: `{s['input']}` -> Resp: {s['response_text']} (Menus: {s['menus_count']})\n")

    print(f"\n✅ Test Complete. Report generated at {REPORT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
