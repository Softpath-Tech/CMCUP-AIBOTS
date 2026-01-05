import sys
import os
import re
import uuid
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --------------------------------------------------
# 1. Ensure Python can find project root (Render-safe)
# --------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# --------------------------------------------------
# 2. Imports
# --------------------------------------------------
from rag.chain import get_rag_chain
from rag.sql_queries import (
    get_participation_stats, 
    get_fixture_details, 
    get_geo_details,
    get_sport_schedule,
    get_disciplines_by_level,
    get_player_venues_by_phone,
    get_player_venue_by_ack,
    get_sport_rules
)
from rag.location_search import search_district_officer, search_cluster_incharge
# Also importing get_player_by_phone from lookup (which uses SQL now)
# rag.lookup imports removed as per privacy policy
from rag.sql_agent import run_sql_agent

# --------------------------------------------------
# 3. Initialize FastAPI App
# --------------------------------------------------
app = FastAPI(
    title="SATG Sports Chatbot API",
    description="Hybrid RAG + SQL Engine for Player Stats & Rules",
    version="1.1.0"
)

# Mount Static Files (Demo UI)
app.mount("/demo", StaticFiles(directory="static", html=True), name="static")

# 4. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# 5. Models and Globals
# --------------------------------------------------
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None  # Added for memory

class WhatsAppChatRequest(BaseModel):
    user_message: str
    first_name: Optional[str] = None
    phone_number: Optional[str] = None

# Global RAG Cache (Lazy Loaded)
rag_chain = None

# In-Memory Chat History: {session_id: [(user, bot), ...]}
CHAT_SESSIONS = {}

# MENU STATE MANAGEMENT
SESSION_STATE = {} # {session_id: current_state_str}
SESSION_DATA = {} # {session_id: {key: val}}

# MENU CONSTANTS
MENU_MAIN = "MAIN_MENU"
MENU_REG_FAQ = "MENU_REG_FAQ"           # 1. Registration FAQ
MENU_DISCIPLINES = "MENU_DISCIPLINES"

MENU_SCHEDULE = "MENU_SCHEDULE"         # 3. Schedules
MENU_VENUES = "MENU_VENUES"             # 4. Venues
MENU_OFFICERS = "MENU_OFFICERS"         # 5. Officers
MENU_PLAYER_STATUS = "MENU_PLAYER_STATUS" # 6. Player Details
MENU_MEDALS = "MENU_MEDALS"             # 7. Medal Tally
MENU_HELPDESK = "MENU_HELPDESK"         # 8. Helpdesk
MENU_LANGUAGE = "MENU_LANGUAGE"         # 9. Language

# INTERMEDIATE GROUP MENUS
MENU_GROUP_SPORTS = "MENU_GROUP_SPORTS"   # Sports & Matches
MENU_GROUP_VENUES = "MENU_GROUP_VENUES"   # Venues & Officials
MENU_GROUP_HELP = "MENU_GROUP_HELP"       # Help & Language

# SUB-MENUS FOR OFFICERS
MENU_OFFICERS_DISTRICT = "MENU_OFFICERS_DISTRICT"
MENU_OFFICERS_CLUSTER = "MENU_OFFICERS_CLUSTER"

# SUB-INTERACTION STATES (Waiting for input)
STATE_WAIT_PHONE = "STATE_WAIT_PHONE"
STATE_WAIT_ACK = "STATE_WAIT_ACK"
STATE_WAIT_LOCATION = "STATE_WAIT_LOCATION"
STATE_WAIT_SPORT_SCHEDULE = "STATE_WAIT_SPORT_SCHEDULE"
STATE_WAIT_SPORT_RULES = "STATE_WAIT_SPORT_RULES"
STATE_WAIT_SPORT_AGE = "STATE_WAIT_SPORT_AGE"
STATE_WAIT_DIST_OFFICER = "STATE_WAIT_DIST_OFFICER"
STATE_WAIT_CLUSTER_INCHARGE = "STATE_WAIT_CLUSTER_INCHARGE"
STATE_WAIT_MANDAL_INCHARGE = "STATE_WAIT_MANDAL_INCHARGE"

MENU_DISCIPLINES_LEVEL = "MENU_DISCIPLINES_LEVEL"
MENU_DISCIPLINES_CATEGORY = "MENU_DISCIPLINES_CATEGORY"
MENU_SELECT_SPORT = "MENU_SELECT_SPORT"
MENU_GAME_OPTIONS = "MENU_GAME_OPTIONS"
MENU_SCHEDULE_GAME_SEARCH = "MENU_SCHEDULE_GAME_SEARCH"

PARENT_MAP = {
    MENU_REG_FAQ: MENU_MAIN,
    MENU_DISCIPLINES: MENU_MAIN,
    MENU_SCHEDULE: MENU_MAIN,
    MENU_VENUES: MENU_MAIN,
    MENU_OFFICERS: MENU_MAIN,
    MENU_PLAYER_STATUS: MENU_MAIN,
    MENU_MEDALS: MENU_MAIN,
    MENU_HELPDESK: MENU_MAIN,
    MENU_LANGUAGE: MENU_MAIN,
    
    # Sub-states
    STATE_WAIT_PHONE: MENU_PLAYER_STATUS, # Back to Player Status menu
    STATE_WAIT_ACK: MENU_PLAYER_STATUS,
    STATE_WAIT_LOCATION: MENU_VENUES,     # Back to Venues menu
    STATE_WAIT_SPORT_SCHEDULE: MENU_SCHEDULE,
    STATE_WAIT_SPORT_RULES: MENU_MAIN, # Or relevant parent
    STATE_WAIT_DIST_OFFICER: MENU_OFFICERS,
    STATE_WAIT_DIST_OFFICER: MENU_OFFICERS,
    STATE_WAIT_CLUSTER_INCHARGE: MENU_OFFICERS,
    STATE_WAIT_MANDAL_INCHARGE: MENU_OFFICERS,
    
    MENU_DISCIPLINES_LEVEL: MENU_MAIN,
    MENU_SELECT_SPORT: MENU_DISCIPLINES,  # Back to Level Selection
    MENU_GAME_OPTIONS: MENU_SELECT_SPORT, # Back to Sport List
    MENU_SCHEDULE_GAME_SEARCH: MENU_SCHEDULE, # Back to Schedules Menu

    # Officers Sub-menus
    MENU_OFFICERS_DISTRICT: MENU_OFFICERS,
    MENU_OFFICERS_CLUSTER: MENU_OFFICERS,

    # Intermediate Groups Back Pointers
    MENU_GROUP_SPORTS: MENU_MAIN,
    MENU_GROUP_VENUES: MENU_MAIN,
    MENU_GROUP_HELP: MENU_MAIN,
}


def get_or_init_rag_chain():
    """
    Lazy-load RAG chain.
    This prevents Render startup timeout.
    """
    global rag_chain
    if rag_chain is None:
        print("🧠 Initializing RAG chain (lazy)...")
        rag_chain = get_rag_chain()
        print("✅ RAG chain initialized")
    return rag_chain

# --------------------------------------------------
# 6. Helpers & Menu Content
# --------------------------------------------------
# --- HELPER: Cluster Search ---
import difflib

def search_cluster_incharge_helper(user_query):
    """
    Searches for the cluster name using fuzzy matching.
    """
    try:
        file_path = "data/new data/Mandal_Incharges_Cleaned.txt"
        if not os.path.exists(file_path):
            return "⚠️ Data file not found."
            
        target = user_query.strip().lower()
        results = []
        
        # 1. Collect all valid clusters and their full lines
        cluster_map = {} # {cluster_lower: [line1, line2]}
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "Cluster:" in line:
                    # Parse: Mandal: ... | Cluster: XYZ | ...
                    parts = line.split("|")
                    if len(parts) >= 2:
                        # Extract " Cluster: XYZ " -> "XYZ"
                        c_raw = parts[1].split(":")[1].strip()
                        c_lower = c_raw.lower()
                        
                        if c_lower not in cluster_map:
                            cluster_map[c_lower] = []
                        cluster_map[c_lower].append(line.strip())
        
        # 2. Exact Match Check
        if target in cluster_map:
            results = cluster_map[target]
            found_name = target
        else:
            # 3. Partial/Substring Match (if target > 3 chars)
            if len(target) > 3:
                for c_name in cluster_map:
                    if target in c_name: # target "Akine" in "Akinepalli"
                        results = cluster_map[c_name]
                        found_name = c_name
                        break
            
            # 4. Fuzzy Match (if no exact or partial match)
            if not results:
                all_clusters = list(cluster_map.keys())
                matches = difflib.get_close_matches(target, all_clusters, n=1, cutoff=0.55) # Lowered slightly to 0.55
                
                if matches:
                    found_name = matches[0]
                    results = cluster_map[found_name]
                else:
                    return None

        # 5. Format Output
        if results:
            # Capitalize the found name for display
            display_name = found_name.title() 
            response = f"**Found In-Charge Details for '{display_name}':**\n\n"
            for res in results[:5]: 
                response += f"🔹 {res}\n"
            return response
            
        return None

    except Exception as e:
        return f"Error searching data: {str(e)}"

# --- MENU TEXT HELPERS ---
def get_menu_text(menu_name):
    print(f"DEBUG: get_menu_text called with {menu_name}")
    if menu_name == MENU_MAIN:
        return (
            "🏆 **Welcome to Telangana Sports Authority – CM Cup 2025 Chatbot** 👋\n\n"
            "I can help players, parents, coaches, and officials.\n\n"
            "1️⃣ Registration & Eligibility\n"
            "2️⃣ Sports & Matches\n"
            "3️⃣ Venues & Officials\n"
            "4️⃣ Player Status\n"
            "5️⃣ Help & Language\n\n"
            "💡 *Type a number (1–5) to proceed*"
        )
    elif menu_name == MENU_GROUP_SPORTS:
        return (
            "🏅 **Sports & Matches**\n\n"
            "1️⃣ Sports Disciplines\n"
            "2️⃣ Schedules & Fixtures\n"
            "3️⃣ Medal Tally\n\n"
            "🔙 *Type 'Back' for Main Menu*"
        )
    elif menu_name == MENU_GROUP_VENUES:
        return (
            "🏟️ **Venues & Officials**\n\n"
            "1️⃣ Venues\n"
            "2️⃣ District Officers\n"
            "3️⃣ Venue In-Charge\n"
            "4️⃣ Mandal In-Charge\n\n"
            "🔙 *Type 'Back' for Main Menu*"
        )
    elif menu_name == MENU_GROUP_HELP:
        return (
            "📞 **Help & Language**\n\n"
            "1️⃣ Helpline Numbers\n"
            "2️⃣ Email Support\n"
            "3️⃣ Change Language\n\n"
            "🔙 *Type 'Back' for Main Menu*"
        )
    elif menu_name == MENU_REG_FAQ:
        return (
            "📝 **Registration & Eligibility**\n\n"
            "1️⃣ How to Register\n"
            "2️⃣ Eligibility Rules\n"
            "3️⃣ Documents Required\n"
            "4️⃣ Registration Status\n"
            "5️⃣ FAQs\n\n"
            "🔙 *Type 'Back' to return to Main Menu*"
        )
    elif menu_name == MENU_DISCIPLINES:
        return (
            "📅 **Disciplines - Select Level**\n\n"
            "1️⃣ Gram Panchayat / Cluster Level\n"
            "2️⃣ Mandal Level\n"
            "3️⃣ Assembly Constituency Level\n"
            "4️⃣ District Level\n"
            "5️⃣ State Level\n\n"
            "🔙 *Type 'Back' for Main Menu*"
        )

    elif menu_name == MENU_SCHEDULE:
        return (
            "🏆 **Schedules**\n\n"
            "1️⃣ Tournament Schedule\n"
            "2️⃣ Games Schedule\n\n"
            "🔙 *Type 'Back' to return to Main Menu*"
        )
    elif menu_name == MENU_VENUES:
        return (
            "📜 **Venues Information**\n\n"
            "⚠️ *Data coming soon for Venues.*"
        )
    elif menu_name == MENU_OFFICERS:
        return (
            "📊 **Special Officers / In-Charge Details**\n\n"
            "1️⃣ District Officers\n"
            "2️⃣ Venue In-Charge\n\n"
            "🔙 *Type 'Back' to return to Main Menu*"
        )
    elif menu_name == MENU_PLAYER_STATUS:
        return (
            "📥 **Player Details / Status**\n\n"
            "1️⃣ Search by Phone No\n"
            "2️⃣ Search by Acknowledgment No\n\n"
            "🔙 *Type 'Back' to return*"
        )
    elif menu_name == MENU_MEDALS:
        return (
            "📍 **Medal Tally**\n\n"
            "🏆 District-wise Medal Tally will be available after the State Meet commences.\n"
            "Stay tuned!"
        )
    elif menu_name == MENU_HELPDESK:
         return (
             "📞 **Helpdesk & Support**\n\n"
             "1️⃣ State Helpline Numbers\n"
             "2️⃣ District Sports Officers\n"
             "3️⃣ Email Support\n\n"
             "🔙 *Type 'Back' for Main Menu*"
         )
    elif menu_name == MENU_LANGUAGE:
         return (
             "🌐 **Select Language**\n\n"
             "1️⃣ English\n"
             "2️⃣ తెలుగు (Telugu)\n"
             "3️⃣ हिन्दी (Hindi)\n\n"
             "🔙 *Type 'Back' for Main Menu*"
         )
    elif menu_name == MENU_OFFICERS_DISTRICT:
        return (
            "👮‍♂️ **District Sports Officers**\n\n"
            "Please enter the **District Name** to find the District Sports Officer details.\n"
            "Example: *'Warangal', 'Khammam', 'Nalgonda'*"
        )
    elif menu_name == MENU_OFFICERS_CLUSTER:
        return (
            "🏟️ **Venue In-Charge (Cluster/Village)**\n\n"
            "Please enter the **Cluster Name** to find the In-Charge details.\n"
            "Example: *'Akinepalli', 'Dammapeta', 'Allipalli'*"
        )
    elif menu_name == "MENU_OFFICERS_MANDAL":
        return (
            "🏫 **Mandal Level In-Charge**\n\n"
            "Please enter the **Mandal Name** to find the Mandal Educational Officer (MEO) details.\n"
            "Example: *'Jainad', 'Bela', 'Bheempoor'*"
        )
    return "Menu not found."

def extract_plain_text(resp) -> str:
    """Try to extract a single answer string from various response shapes."""
    if resp is None:
        return ""
    
    # If it's a dict, extract text from it
    if isinstance(resp, dict):
        return _extract_from_dict(resp)
        
    # If it's a list/tuple, extract from first item
    if isinstance(resp, (list, tuple)):
        return _extract_from_list(resp)

    # Convert to string
    s = str(resp).strip()
    
    # RECURSIVE PARSING: If the string ITSELF looks like a JSON dict, parse it!
    # Check for both standard JSON {"key": "val"} and Python Dict {'key': 'val'}
    if (s.startswith("{") and s.endswith("}")):
        # 1. Try JSON
        try:
            import json
            parsed = json.loads(s)
            # Recursively extract from the parsed dict
            return extract_plain_text(parsed)
        except:
            # 2. Try Python Literal (for single quotes)
            try:
                import ast
                parsed = ast.literal_eval(s)
                if isinstance(parsed, dict):
                    return extract_plain_text(parsed)
            except:
                pass
                
    return s

def _extract_from_dict(d: dict) -> str:
    # Preferred scalar keys
    for key in ("response", "answer", "text", "content", "message", "output", "result"):
        v = d.get(key)
        # If we find a value, we must potentially UNWRAP it again if it's a JSON string
        if v:
            return extract_plain_text(v)
            
    for key in ("choices", "outputs", "results"):
        if key in d:
            return extract_plain_text(d[key])
            
    # Heuristic: return the first string value found
    for v in d.values():
        candidate = extract_plain_text(v)
        if candidate and candidate != "None" and len(candidate) > 0:
            return candidate
    return ""

def _extract_from_list(lst) -> str:
    for item in lst:
        candidate = extract_plain_text(item)
        if candidate:
            return candidate
    try:
        return " ".join([str(x) for x in lst])
    except Exception:
        return ""

# --------------------------------------------------
# 7. Health Check
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "SATG Chatbot Engine is Running 🚀"
    }

# --------------------------------------------------
# 8. Main Chat Endpoint (Hybrid Router)
# --------------------------------------------------
async def process_user_query(raw_query: str, session_id: str = None):
    """
    Unified Logic Handler: Menu -> SQL -> RAG
    """
    user_query = raw_query.strip().lower()
    # session_id passed as argument
    
    # ------------------------------------------------
    # 0. MENU STATE MACHINE
    # ------------------------------------------------
    
    # Global Exit Commands
    if user_query in ["0", "exit", "quit"]:
         SESSION_STATE.pop(session_id, None)
         return {"response": "👋 Chat Session Ended. Type 'Hi' to start again.", "source": "menu_system"}

    # Global Reset (Home) Commands
    if user_query in ["hi", "hello", "menu", "start", "restart", "home"]:
        if session_id:
            SESSION_STATE[session_id] = MENU_MAIN
        return {"response": get_menu_text(MENU_MAIN), "source": "menu_system"}
        
    # Get Current State
    current_state = SESSION_STATE.get(session_id, MENU_MAIN) if session_id else MENU_MAIN
    
    # Global Back Command
    if user_query in ["back", "previous", "return", "exit"]:
        # Logic to return to parent
        if current_state == MENU_MAIN:
            return {"response": "You are already at the Main Menu.", "source": "menu_system"}
        else:
            # Look up parent
            parent = PARENT_MAP.get(current_state, MENU_MAIN)
            if session_id:
                SESSION_STATE[session_id] = parent
            return {"response": get_menu_text(parent), "source": "menu_system"}

    # State: WAITING FOR INPUT (Phone, Ack, Location)
    # If we are in a 'waiting' state, we treat the query as the input value
    if current_state == STATE_WAIT_PHONE:
        # Check if it looks like a phone number
        if re.search(r'\b[6-9]\d{9}\b', user_query):
            # Direct Lookup Logic
            phone = re.search(r'\b[6-9]\d{9}\b', user_query).group(0)
            print(f"⚡ Intent: Menu Phone Lookup ({phone})")
            
            # Reset state
            if session_id: SESSION_STATE[session_id] = MENU_PLAYER_STATUS
            
            # SQL Lookup
            registrations = get_player_venues_by_phone(phone)
            
            if not registrations:
                 return {"response": f"ℹ️ No registrations found for **{phone}**. Please check the number or register at the official site.", "source": "sql_database"}
            
            # Logic: 1 Record vs Multi
            if len(registrations) == 1:
                rec = registrations[0]
                venue = rec.get('venue')
                sport = rec.get('sport_name') or rec.get('event_name')
                
                txt = f"### 🏟️ Venue Details for {sport}\n"
                if venue:
                    txt += f"**Venue:** {venue}\n"
                    txt += f"**Date:** {rec.get('match_date') or 'Check Schedule'}\n"
                else:
                    txt += "**Status:** Venue details pending/TBD.\n"
                
                # Always show In-Charge if available
                if rec.get('cluster_incharge'):
                     txt += f"\n👤 **Venue In-Charge:** {rec.get('cluster_incharge')}\n"
                     txt += f"📞 **Contact:** {rec.get('incharge_mobile', 'N/A')}\n"
                
                return {"response": txt, "source": "sql_database"}
                
            else:
                # Multiple Records
                txt = f"found **{len(registrations)} registrations** for this number:\n"
                for r in registrations:
                    s = r.get('sport_name') or r.get('event_name')
                    txt += f"- {s}\n"
                
                txt += "\nSince you have multiple events, please provide your **Acknowledgment Number** (e.g., SATGCMC-...) to get specific venue details."
                return {"response": txt, "source": "sql_database"} 
        else:
             return {"response": "❌ Invalid Phone Number. Please enter a 10-digit mobile number starting with 6-9.\n\nType 'Back' to cancel.", "source": "validation_error"}
    
    # State: WAITING FOR LOCATION
    if current_state == STATE_WAIT_LOCATION:
        loc_name = user_query
        print(f"⚡ Intent: Menu Location Lookup ({loc_name})")
        # Keep state to allow checking another location
        
        try:
            res = get_geo_details(loc_name)
            if res:
                t = res['type']
                d = res['data']
                txt = f"### 📍 Location Found: {d.get('vill_nm') or d.get('mandal_nm') or d.get('dist_nm')}\n"
                txt += f"**Type:** {t}\n"
                if t == 'Village':
                    txt += f"**Mandal:** {d.get('parent_mandal')}\n"
                    txt += f"**District:** {d.get('parent_district')}"
                elif t == 'Mandal':
                    txt += f"**District:** {d.get('parent_district')}"
                
                txt += "\n\nType another location to check, or 'Back'."
                return {"response": txt, "source": "sql_database"}
            else:
                return {"response": f"🚫 **{loc_name}** could not be found in our database.\n\nType another name or 'Back'.", "source": "sql_database"}
        except Exception as e:
            return {"response": f"Error looking up location: {str(e)}", "source": "error"}

    # State: WAITING FOR SPORT (SCHEDULE)
    if current_state == STATE_WAIT_SPORT_SCHEDULE:
        sport_name = user_query
        print(f"⚡ Intent: Menu Sport Schedule ({sport_name})")
        # REMOVED RESET: Allow continuous querying (e.g. Cricket then Kabaddi)
        # if session_id: SESSION_STATE[session_id] = MENU_SCHEDULE
        
        try:
             schedules = get_sport_schedule(sport_name)
             if schedules:
                 txt = f"### 📅 {sport_name.title()} Schedule (Next 5)\n"
                 for m in schedules[:5]:
                     txt += f"- **{m.get('event_name')}**: {m.get('team1_name')} vs {m.get('team2_name')} @ {m.get('venue')}\n"
                 return {"response": txt, "source": "sql_database"}
             else:
                 return {"response": f"ℹ️ No specific schedule found for **{sport_name}**. It might not be scheduled yet or check spelling.\n\nType another sport or 'Back'.", "source": "sql_database"}
        except Exception as e:
             return {"response": f"Error retrieving schedule: {str(e)}", "source": "error"}

    # State: WAITING FOR SPORT (AGE CRITERIA)
    if current_state == STATE_WAIT_SPORT_AGE:
        sport_input = user_query
        print(f"⚡ Intent: Age Criteria Lookup ({sport_input})")
        
        try:
            rules = get_sport_rules(sport_input)
            if rules:
                txt = f"### 🎂 Age Criteria for {rules.get('sport_name')}\n\n"
                txt += f"**Min Age:** {rules.get('min_age')} years\n"
                txt += f"**Max Age:** {rules.get('max_age')} years\n"
                txt += f"**Team Size:** {rules.get('team_size') or 'Individual'}\n"
                txt += f"**Para Event:** {'Yes' if rules.get('is_para')=='1' else 'No'}\n\n"
                txt += "Type another sport to check, or 'Back'."
                return {"response": txt, "source": "sql_database"}
            else:
                return {"response": f"ℹ️ Could not find rules for **{sport_input}**. Please check the spelling or try another sport.", "source": "sql_database"}
        except Exception as e:
            return {"response": f"Error looking up age rules: {e}", "source": "error"}


    # State: WAITING FOR SPORT (RULES)
    if current_state == STATE_WAIT_SPORT_RULES:
        sport_name = user_query
        print(f"⚡ Intent: Menu Sport Rules ({sport_name})")
        
        try:
            rag_bot = get_or_init_rag_chain()
            rag_query = f"What are the age limits, eligibility and team rules for {sport_name} in CM Cup 2025?"
            rag_resp = rag_bot.invoke({"question": rag_query})
            rag_text = extract_plain_text(rag_resp.get('result', rag_resp))
            return {"response": f"📜 **Rules for {sport_name}:**\n\n{rag_text}", "source": "rag_chain"}
        except Exception as e:
             return {"response": f"Error retrieving rules: {str(e)}", "source": "error"}

    # State: WAITING FOR DISTRICT OFFICER
    if current_state == STATE_WAIT_DIST_OFFICER:
        district_name = user_query
        print(f"⚡ Intent: District Officer Lookup ({district_name})")
        
        try:
             # Lazy import for safety
            from rag.location_search import search_district_officer
            officer = search_district_officer(district_name)
            
            if officer:
                if session_id: SESSION_STATE[session_id] = MENU_OFFICERS_DISTRICT
                
                # Format output properly
                txt = f"### 👮‍♂️ District Sports Officer - {officer.get('district_name')}\n\n"
                txt += f"**Name:** {officer.get('special_officer_name')}\n"
                txt += f"**Designation:** {officer.get('designation')}\n"
                txt += f"**Contact:** {officer.get('contact_no')}\n\n"
                txt += "Type another District Name or 'Back'."
                return {"response": txt, "source": "file_search"}
            else:
                return {"response": f"ℹ️ No District Sports Officer found for **{district_name}**. Please check the spelling or try another district.\n\nType another district or 'Back'.", "source": "file_search"}
        except Exception as e:
            return {"response": f"Error searching for district officer: {str(e)}", "source": "error"}

    # State: WAITING FOR CLUSTER INCHARGE
    if current_state == STATE_WAIT_CLUSTER_INCHARGE:
        cluster_name = user_query
        print(f"⚡ Intent: Cluster In-Charge Lookup ({cluster_name})")
        
        try:
            # Lazy import for safety
            from rag.location_search import search_cluster_incharge
            
            # Correct function name
            res = search_cluster_incharge(cluster_name)
            
            if res:
                if session_id: SESSION_STATE[session_id] = MENU_OFFICERS_CLUSTER
                
                t = res.get('type', 'Cluster')
                d = res.get('data', {})
                
                if t == 'Village':
                     txt = f"### 🏟️ Venue In-Charge (Village: {d.get('villagename')})\n"
                     txt += f"mapped to **Cluster: {res.get('mapped_cluster')}**\n\n"
                else:
                     txt = f"### 🏟️ Venue In-Charge (Cluster: {d.get('clustername')})\n\n"
                
                txt += f"**In-Charge:** {d.get('incharge_name')}\n"
                txt += f"**Contact:** {d.get('mobile_no')}\n\n"
                txt += "Type another Cluster/Village Name or 'Back'."
                return {"response": txt, "source": "file_search"}
            else:
                return {"response": f"ℹ️ No Venue In-Charge found for **{cluster_name}**. Please check the spelling or try another cluster.\n\nType another cluster or 'Back'.", "source": "file_search"}
        except Exception as e:
            return {"response": f"Error searching for cluster in-charge: {str(e)}", "source": "error"}

    # State: WAITING FOR MANDAL INCHARGE
    if current_state == STATE_WAIT_MANDAL_INCHARGE:
        mandal_name = user_query
        print(f"⚡ Intent: Mandal In-Charge Lookup ({mandal_name})")
        
        try:
            # Lazy import
            from rag.location_search import search_mandal_incharge
            
            res = search_mandal_incharge(mandal_name)
            
            if res:
                if session_id: SESSION_STATE[session_id] = "MENU_OFFICERS_MANDAL"
                
                txt = f"### 🏫 Mandal In-Charge (MEO) - {res.get('mandal_name')}\n\n"
                txt += f"**Name:** {res.get('incharge_name')}\n"
                txt += f"**District:** {res.get('district_name')}\n"
                txt += f"**Mobile:** {res.get('mobile_no', 'N/A')}\n\n"
                txt += "Type another Mandal Name or 'Back'."
                return {"response": txt, "source": "file_search"}
            else:
                return {"response": f"ℹ️ No Mandal In-Charge found for **{mandal_name}**. Please check the spelling or try another mandal.\n\nType another mandal or 'Back'.", "source": "file_search"}
        except Exception as e:
            return {"response": f"Error searching for mandal in-charge: {str(e)}", "source": "error"}

    # State Handling Logic
    if user_query.isdigit():
        choice = int(user_query)
        
        if current_state == MENU_MAIN:
            if choice == 1:
                # Registration & Eligibility
                if session_id: SESSION_STATE[session_id] = MENU_REG_FAQ
                return {"response": get_menu_text(MENU_REG_FAQ), "source": "menu_system"}
            elif choice == 2:
                # Sports & Matches -> Submenu
                if session_id: SESSION_STATE[session_id] = MENU_GROUP_SPORTS
                return {"response": get_menu_text(MENU_GROUP_SPORTS), "source": "menu_system"}
            elif choice == 3:
                # Venues & Officials -> Submenu
                if session_id: SESSION_STATE[session_id] = MENU_GROUP_VENUES
                return {"response": get_menu_text(MENU_GROUP_VENUES), "source": "menu_system"}
            elif choice == 4:
                # Player Status
                if session_id: SESSION_STATE[session_id] = MENU_PLAYER_STATUS
                return {"response": get_menu_text(MENU_PLAYER_STATUS), "source": "menu_system"}
            elif choice == 5:
                # Help & Language -> Submenu
                if session_id: SESSION_STATE[session_id] = MENU_GROUP_HELP
                return {"response": get_menu_text(MENU_GROUP_HELP), "source": "menu_system"}
        
        # --- INTERMEDIATE GROUPS ---
        elif current_state == MENU_GROUP_SPORTS:
            if choice == 1:
                if session_id: SESSION_STATE[session_id] = MENU_DISCIPLINES
                return {"response": get_menu_text(MENU_DISCIPLINES), "source": "menu_system"}
            elif choice == 2:
                if session_id: SESSION_STATE[session_id] = MENU_SCHEDULE
                return {"response": get_menu_text(MENU_SCHEDULE), "source": "menu_system"}
            elif choice == 3:
                if session_id: SESSION_STATE[session_id] = MENU_MEDALS
                return {"response": get_menu_text(MENU_MEDALS), "source": "menu_system"}

        elif current_state == MENU_GROUP_VENUES:
            # 1. Venues, 2. Dist Officers, 3. Cluster In-Charge
            if choice == 1:
                 if session_id: SESSION_STATE[session_id] = MENU_VENUES
                 return {"response": get_menu_text(MENU_VENUES), "source": "menu_system"}
            elif choice == 2:
                 try:
                     if session_id: SESSION_STATE[session_id] = STATE_WAIT_DIST_OFFICER
                     # Using literal string to prevent potential NameError if constant is missing in runtime env
                     return {"response": get_menu_text("MENU_OFFICERS_DISTRICT"), "source": "menu_system"}
                 except Exception as e:
                     print(f"CRASH in Option 2: {e}")
                     return {"response": f"❌ Error loading District Officers menu: {str(e)}", "source": "error_handler"}
            elif choice == 3:
                 try:
                     if session_id: SESSION_STATE[session_id] = STATE_WAIT_CLUSTER_INCHARGE
                     return {"response": get_menu_text("MENU_OFFICERS_CLUSTER"), "source": "menu_system"}
                 except Exception as e:
                     print(f"CRASH in Option 3: {e}")
                     return {"response": f"❌ Error loading Venue In-Charge menu: {str(e)}", "source": "error_handler"}
            elif choice == 4:
                 try:
                     if session_id: SESSION_STATE[session_id] = STATE_WAIT_MANDAL_INCHARGE
                     return {"response": get_menu_text("MENU_OFFICERS_MANDAL"), "source": "menu_system"}
                 except Exception as e:
                     print(f"CRASH in Option 4: {e}")
                     return {"response": f"❌ Error loading Mandal In-Charge menu: {str(e)}", "source": "error_handler"}
        
        elif current_state == MENU_GROUP_HELP:
             if choice == 1:
                 # Helpline Numbers
                 return {"response": "📞 **Helpline Numbers:**\n\nState Control Room: **040-12345678**\nWhatsApp Support: **+91-9876543210**", "source": "static_info"}
             elif choice == 2:
                 # Email Support
                 return {"response": "📧 **Email Support:**\n\nPlease reach us at: **support@cmcup.telangana.gov.in**", "source": "static_info"}
             elif choice == 3:
                 if session_id: SESSION_STATE[session_id] = MENU_LANGUAGE
                 return {"response": get_menu_text(MENU_LANGUAGE), "source": "menu_system"}

        if current_state == MENU_OFFICERS:
            # Deprecated direct access but keeping compliant just in case
            pass
        
        # --- SUB MENU: LANGUAGE ---
        elif current_state == MENU_LANGUAGE:
            resp_text = ""
            if choice == 1:
                resp_text = "✅ **Language set to English**.\n\nType 'Menu' to go back to main menu."
            elif choice == 2:
                resp_text = "✅ **భాష తెలుగుకి మార్చబడింది** (Language set to Telugu).\n\nప్రధాన మెనూకి వెళ్లడానికి 'Menu' అని టైప్ చేయండి."
            elif choice == 3:
                resp_text = "✅ **भाषा हिंदी में सेट की गई है** (Language set to Hindi).\n\nमुख्य मेनू पर जाने के लिए 'Menu' टाइप करें."
            else:
                resp_text = "❌ Invalid Option. Please select 1, 2, or 3."
            
            # Since we don't have real multi-lingual support yet, just acknowledging
            return {"response": resp_text, "source": "menu_system"}

        
        # --- SUB MENU: DISCIPLINES (LEVEL Selection) ---
        elif current_state == MENU_DISCIPLINES:
            level_map = {
                1: "cluster",
                2: "mandal",
                3: "assembly",
                4: "district",
                5: "state"
            }
            if choice in level_map:
                level_name = level_map[choice]
                try:
                    from rag.sql_queries import get_disciplines_by_level
                    games = get_disciplines_by_level(level_name)
                    
                    # Display titles mapping
                    titles = {
                        "cluster": "Cluster / Gram Panchayat Level",
                        "mandal": "Mandal Level",
                        "assembly": "Assembly Constituency Level",
                        "district": "District Level",
                        "state": "State Level"
                    }
                    display_title = titles.get(level_name, level_name.title() + " Level")

                    if games:
                        # Store in Session Data
                        if session_id:
                            SESSION_STATE[session_id] = MENU_SELECT_SPORT
                            SESSION_DATA[session_id] = {"sports": games, "level_title": display_title}

                        txt = f"### 🏅 Sports at {display_title}\n\n"
                        for i, g in enumerate(games, 1):
                            txt += f"{i}. {g}\n"
                        txt += "\nℹ️ *Select a number to view details (Age, Events, Rules)*"
                        return {"response": txt, "source": "sql_database"}
                    else:
                         return {"response": f"ℹ️ No sports found specifically for **{display_title}** in the database.", "source": "sql_database"}
                except Exception as e:
                    print(f"Error fetching disciplines: {e}")
                    return {"response": "❌ An error occurred while fetching disciplines. Please try again.", "source": "error_handler"}

        # --- SUB MENU: SELECT SPORT (Drill Down) ---
        elif current_state == MENU_SELECT_SPORT:
            data = SESSION_DATA.get(session_id, {})
            sports = data.get("sports", [])
            
            # Check if valid index
            if 1 <= choice <= len(sports):
                selected_sport = sports[choice - 1]
                
                # Store selected sport
                if session_id:
                     SESSION_STATE[session_id] = MENU_GAME_OPTIONS
                     SESSION_DATA[session_id]["selected_sport"] = selected_sport
                
                return {
                    "response": (
                        f"🏅 **{selected_sport}** - Options\n\n"
                        "1️⃣ Age Criteria\n"
                        "2️⃣ Events of the Game\n"
                        "3️⃣ Rules of Game\n\n"
                        "🔙 *Type 'Back' to list sports again*"
                    ),
                    "source": "menu_system"
                }
            else:
                 return {"response": "❌ Invalid Option. Please select a number from the list above.", "source": "validation_error"}

        # --- SUB MENU: GAME OPTIONS (Age, Events, Rules) ---
        elif current_state == MENU_GAME_OPTIONS:
            data = SESSION_DATA.get(session_id, {})
            selected_sport = data.get("selected_sport", "Unknown Sport")
            
            from rag.sql_queries import get_discipline_info, get_categories_by_sport
            
            info = get_discipline_info(selected_sport)
            game_id = info['game_id'] if info else None

            if choice == 1: # Age Criteria
                if not game_id:
                     return {"response": f"ℹ️ No detailed age info found for **{selected_sport}**.", "source": "sql_database"}
                
                cats = get_categories_by_sport(game_id)
                if cats:
                     txt = f"### 🎂 Age Criteria for {selected_sport}\n\n"
                     for c in cats:
                         gender_map = {1: "Male", 2: "Female"}
                         g_str = gender_map.get(c['gender'], "Open")
                         txt += f"- **{c['cat_name']}** ({g_str}): {c['from_age']} - {c['to_age']} Years\n"
                     return {"response": txt, "source": "sql_database"}
                else:
                     return {"response": f"ℹ️ No specific age categories found for **{selected_sport}**.", "source": "sql_database"}

            elif choice == 2: # Events
                if not game_id:
                     return {"response": "ℹ️ Link not available.", "source": "error"}
                
                url = f"https://satg.telangana.gov.in/cmcup/showDisciplineEvents/{game_id}"
                return {
                    "response": (
                        f"🏆 **Events for {selected_sport}**\n\n"
                        f"Please visit the official link below to view all events:\n"
                        f"👉 [View Events for {selected_sport}]({url})"
                    ),
                    "source": "static_link"
                }

            elif choice == 3: # Rules
                 return {"response": "📜 **Rules of Game**\n\nThe rulebook is currently being updated. Please check back later!", "source": "static_placeholder"}

        # --- SUB MENU: REGISTRATION ---
        # --- SUB MENU: REGISTRATION (PLAYER DETAILS) ---
        # --- SUB MENU: PLAYER STATUS ---
        elif current_state == MENU_PLAYER_STATUS:
            if choice == 1:
                # Search by Phone No
                if session_id: SESSION_STATE[session_id] = STATE_WAIT_PHONE
                return {"response": "📱 **Search by Phone No**\n\nPlease enter your registered **Mobile Number** (10 digits).", "source": "menu_system"}
            elif choice == 2:
                # Search by Acknowledgment No
                if session_id: SESSION_STATE[session_id] = STATE_WAIT_ACK
                return {"response": "🔢 **Search by Acknowledgment No**\n\nPlease enter your **Acknowledgment Number** (e.g., SATGCMC-...).", "source": "menu_system"}

        # --- SUB MENU: DISCIPLINES ---
        elif current_state == MENU_DISCIPLINES:
            level_map = {1: "cluster", 2: "mandal", 3: "assembly", 4: "district", 5: "state"}
            if choice in level_map:
                from rag.sql_queries import get_disciplines_by_level
                lvl_name = level_map[choice]
                discs = get_disciplines_by_level(lvl_name)
                
                txt = f"🏆 **Disciplines at {lvl_name.title()} Level:**\n\n"
                if discs:
                    for d in discs:
                        txt += f"• {d.get('dist_game_nm')}\n"
                    txt += "\nType a **Sport Name** for rules or schedule."
                else:
                    txt += "ℹ️ No specific disciplines listed for this level yet."
                return {"response": txt, "source": "sql_database"}
        
        # --- SUB MENU: REG FAQ ---
        elif current_state == MENU_REG_FAQ:
            if choice == 1: # How to Register
                return {"response": "**To Register:**\nVisit [https://satg.telangana.gov.in/cmcup](https://satg.telangana.gov.in/cmcup) and select 'New Registration'.", "source": "static"}
            elif choice == 2: # Eligibility Rules
                # Reuse Age/Rules logic? Or static text? Using static summary + prompt for specifics.
                return {"response": "📋 **Eligibility Rules:**\n\n- Age: 15-35 Years.\n- Must be a resident of Telangana.\n- Cannot represent multiple units.\n\nType 'Back' to return.", "source": "static"}
            elif choice == 3: # Documents
                return {"response": "**Documents Required:**\nAadhar Card, Photo, and Address Proof.", "source": "static"}
            elif choice == 4: # Registration Status
                 return {"response": "🔍 **Check Registration Status:**\n\nPlease use **Option 4 (Player Status)** from the Main Menu to search by Phone or Acknowledgment Number.\n\nType 'Back' for Main Menu.", "source": "redirect"}
            elif choice == 5: # FAQs
                 return {"response": "❓ **General FAQs:**\n\n- *Is it free?* Yes.\n- *Can I play multiple sports?* Yes, if schedules allow.\n- *Where to report?* Check Venue details.\n\nType 'Back' to return.", "source": "static"}

        

        # --- SUB MENU: SCHEDULE ---
        # --- SUB MENU: SCHEDULE ---
        elif current_state == MENU_SCHEDULE:
            if choice == 1:
                # Tournament Schedule (Static)
                return {
                    "response": (
                        "🗓️ **Tournament Schedule**\n\n"
                        "🔸 **Gram Panchayat / Cluster:** 17 Jan - 22 Jan 2026\n"
                        "🔸 **Mandal Level:** 28 Jan - 31 Jan 2026\n"
                        "🔸 **Assembly Constituency:** 03 Feb - 07 Feb 2026\n"
                        "🔸 **District Level:** 10 Feb - 14 Feb 2026\n"
                        "🔸 **State Level:** 19 Feb - 26 Feb 2026\n\n"
                        "🔙 *Type 'Back' to return to Main Menu*"
                    ),
                    "source": "static_data"
                }
            elif choice == 2:
                # Games Schedule (Game Search)
                if session_id: SESSION_STATE[session_id] = MENU_SCHEDULE_GAME_SEARCH
                return {
                    "response": (
                        "🏅 **Games Schedule**\n\n"
                        "Please enter the Name of the Game you are looking for.\n"
                        "Example: *Kabaddi, Athletics, Cricket*"
                    ),
                    "source": "menu_system"
                }

        # --- SUB MENU: SCHEDULE GAME SEARCH (TEXT INPUT) ---
        elif current_state == MENU_SCHEDULE_GAME_SEARCH:
             pass 
             
        # --- SUB MENU: OFFICERS ---
        elif current_state == MENU_OFFICERS:
            pass


        # Catch-all for invalid numbers in a menu context
        return {"response": "❌ Invalid Option. Please select a valid number from the menu or type 'Back'.", "source": "menu_system"}

    # ------------------------------------------------
    # END MENU MACHINE (DIGIT HANDLING)
    # ------------------------------------------------

    # --- TEXT INPUT HANDLING FOR MENUS ---
    if current_state == MENU_SCHEDULE_GAME_SEARCH and not user_query.isdigit():
        from rag.sql_queries import get_discipline_info
        info = get_discipline_info(user_query)
        
        if info:
             game_id = info['game_id']
             game_name = info['dist_game_nm']
             url = f"https://satg.telangana.gov.in/cmcup/viewschedulegames/{game_id}"
             return {
                 "response": (
                     f"🗓️ **Schedule for {game_name}**\n\n"
                     f"You can view the specific schedule and fixtures here:\n"
                     f"👉 [View {game_name} Schedule]({url})"
                 ),
                 "source": "sql_database"
             }
        else:
             return {
                 "response": f"❌ Could not find a game named '**{user_query}**'.\nPlease check the spelling (e.g., 'Athletics', 'Kabaddi') and try again.", 
                 "source": "sql_database"
             }

    if current_state == MENU_OFFICERS and not user_query.isdigit():
        # User entered cluster name?
        result = search_cluster_incharge(user_query)
        if result:
            return {"response": result, "source": "local_data_file"}
        else:
            return {"response": f"❌ I couldn't find a cluster named '**{user_query}**'.\nPlease check the spelling or try another cluster name.", "source": "local_data_file"}

    # --- SUB MENU: VENUES (Text Input) ---
    if current_state == MENU_VENUES and not user_query.isdigit():
        pass

            
    
    # ------------------------------------------------
    # END MENU MACHINE -> FALLTHROUGH TO LOGIC
    # ------------------------------------------------

    # 0. Static Data Interceptor
    # 0.1 Year/Version Mismatch Interceptor (High Priority)
    # If user asks for past years (e.g. 2015, 2024), redirect to 2025.
    year_match = re.search(r'\b(20\d{2})\b', user_query)
    if year_match:
        year = int(year_match.group(1))
        if year != 2025 and ("cm" in user_query or "cup" in user_query):
             return {
                 "response": f"ℹ️ **Note:** I currently only have information for the **Key Minister's Cup (CM Cup) 2025**. I don't have data for {year}.",
                 "source": "logic_interceptor"
             }

    # 0.2 Static Data Interceptor - DISABLED BY USER REQUEST
    # All queries now proceed to logic interceptors, SQL, or RAG LLM.
    pass

    # 0.4 Age / Rules Lookup Interceptor
    # Pattern 1: "Age limit for Fencing", "Age criteria of Kabaddi"
    age_pattern = re.search(r'(?:age|limit|criteria).*(?:for|of|in|limits?)\s+([a-zA-Z]+)', user_query)
    # Pattern 2: "Fencing age", "Kabaddi limits"
    age_pattern_2 = re.search(r'^([a-zA-Z]+)\s+(?:age|limits?|criteria)', user_query)

    detected_sport = None
    if age_pattern: detected_sport = age_pattern.group(1)
    elif age_pattern_2: detected_sport = age_pattern_2.group(1)

    # Filter out common false positives
    ignored_sports = ["player", "participation", "total", "registration", "the", "my", "our", "your", "any"]
    
    if detected_sport and detected_sport not in ignored_sports and len(detected_sport) > 2:
        try:
            rules = get_sport_rules(detected_sport)
            if rules:
                txt = f"### 🎂 Age Criteria for {rules.get('sport_name')}\n\n"
                txt += f"**Min Age:** {rules.get('min_age')} years\n"
                txt += f"**Max Age:** {rules.get('max_age')} years\n"
                txt += f"**Team Size:** {rules.get('team_size') or 'Individual'}\n"
                txt += f"**Level:** {rules.get('level', 'N/A')}\n"
                txt += f"**Para Event:** {'Yes' if rules.get('is_para')=='1' else 'No'}\n\n"
                txt += "Type 'Rules' for more details or another sport name."
                return {"response": txt, "source": "sql_interceptor"}
        except Exception as e:
            print(f"Error in Age Interceptor: {e}")

    # 0.5 Participation Stats (New)
    # Check for general count queries, but exclude "rules" or "limit" type queries (e.g., "how many players can register")
    stats_keywords = ["total participation", "how many players", "total registration", "total players", "no participation"]
    rule_exclusions = ["can", "limit", "allow", "eligible", "team size", "per team"]
    
    if any(k in user_query for k in stats_keywords) and not any(e in user_query for e in rule_exclusions):
        from rag.sql_queries import get_participation_stats
        count = get_participation_stats()
        return {
            "response": f"📊 **Participation Status:**\n\nA total of **{count} players** have registered for the Chief Minister's Cup (CM Cup) 2025 so far!",
            "model_used": "sql_database"
        }

    # 1. Phone Number match - PRIVACY WARNING

    # 0.6 Registration/Ack Number Link
    if "acknowledgment number" in user_query or "acknowledgement number" in user_query or "ack number" in user_query or "ack no" in user_query:
        if "what is" in user_query or "download" in user_query or "get" in user_query:
            return {
                "response": "📥 **Download Acknowledgment:**\n\nYou can find and download your Acknowledgment Number from the official website:\n\n👉 [Download Enrollment Acknowledgment](https://satg.telangana.gov.in/cmcup/downloadack)",
                "source": "static_rule"
            }

    # 1. Phone Number match - PRIVACY GUARD & VENUE FLOW
    original_query = raw_query.strip() # Keep casing for Reg IDs if needed
    
    # Define venue intent keywords (Fix for NameError)
    venue_keywords = ["venue", "status", "application", "check", "where", "game status", "match status"]
    venue_intent = any(k in user_query for k in venue_keywords)

    phone_match = re.search(r'\b[6-9]\d{9}\b', original_query)
    
    # 1A. Venue/Status Flow (Exception to Filter)
    # 1A. Venue/Status Flow (Implicit if phone number provided)
    # venue_intent is now optional if phone number is present
    
    if phone_match:
        phone = phone_match.group(0)
        print(f"⚡ Intent: Venue Lookup via Phone ({phone})")
        
        # SQL Lookup
        registrations = get_player_venues_by_phone(phone)
        
        if not registrations:
             return {"response": f"ℹ️ No registrations found for **{phone}**. Please check the number or register at the official site.", "source": "sql_database"}
        
        # Logic: 1 Record vs Multi
        if len(registrations) == 1:
            rec = registrations[0]
            venue = rec.get('venue')
            sport = rec.get('sport_name') or rec.get('event_name')
            
            txt = f"### 🏟️ Venue Details for {sport}\n"
            if venue:
                txt += f"**Venue:** {venue}\n"
                txt += f"**Date:** {rec.get('match_date') or 'Check Schedule'}\n"
            else:
                txt += "**Status:** There are no Venue Details available yet.\n"
                txt += f"You can contact your cluster Incharge:\n"
                txt += f"👤 **{rec.get('cluster_incharge', 'N/A')}**\n"
                txt += f"📞 **{rec.get('incharge_mobile', 'N/A')}**\n"
            
            return {"response": txt, "source": "sql_database"}
            
        else:
            # Multiple Records
            txt = f"found **{len(registrations)} registrations** for this number:\n"
            for r in registrations:
                s = r.get('sport_name') or r.get('event_name')
                txt += f"- {s}\n"
            
            txt += "\nSince you have multiple events, please provide your **Acknowledgment Number** (e.g., SATGCMC-...) to get specific venue details."
            return {"response": txt, "source": "sql_database"}

            txt += "\nSince you have multiple events, please provide your **Acknowledgment Number** (e.g., SATGCMC-...) to get specific venue details."
            return {"response": txt, "source": "sql_database"}
    
    # 1C. Venue Intent BUT NO Phone -> Prompt
    # If user mentions venue/status/game but didn't provide phone, prompt them.
    # We use a broad check but ensure it's not a general question like "Where is the venue for Cricket?" (which might be generic).
    # Heuristic: If query is short OR has "my/check", prompt.
    if venue_intent:
        words = user_query.split()
        # Exclude general queries about levels, dates, or schedule
        is_general_query = any(k in user_query for k in ["level", "date", "when", "schedule", "time", "mandal", "district", "cluster", "state", "village", "gram", "panchayat"])
        
        if (len(words) < 8 or "my" in user_query or "check" in user_query or "know" in user_query) and not is_general_query:
             return {
                 "response": "To check your **Venue** or **Game Status**, please provide your registered **Phone Number**.\n\nExample: *Venue details for 9848012345*",
                 "source": "logic_interceptor"
             }

    # 2. Registration ID / Ack No -> Venue Lookup
    ack_match = re.search(r'\b(SATGCMC(?:\d+)?-\d+)\b', original_query, re.IGNORECASE)
    if ack_match:
        ack_no = ack_match.group(1).upper()
        if venue_intent or True: # Always treat Ack No as a lookup request now? Or only if venue intent? User said "Venue Details - Based on Acknowledgement Details". Let's assume lookup.
             print(f"⚡ Intent: Ack No Lookup ({ack_no})")
             rec = get_player_venue_by_ack(ack_no)
             if rec:
                venue = rec.get('venue')
                sport = rec.get('sport_name') or rec.get('event_name')
                
                # Parse Level
                level_str = "Cluster/Village Level"
                if rec.get('is_state_level') == '1': level_str = "Selected for State Level 🏆"
                elif rec.get('is_district_level') == '1': level_str = "Selected for District Level 🥇"
                elif rec.get('is_mandal_level') == '1': level_str = "Selected for Mandal Level 🥈"
                
                txt = f"### 👤 Player Details Found\n"
                txt += f"**Name:** {rec.get('player_nm', 'N/A')}\n"
                txt += f"**Reg ID:** {rec.get('player_reg_id', ack_no)}\n\n"
                
                # Format Location (Remove None/N/A)
                loc_parts = [
                    rec.get('villagename'),
                    rec.get('mandalname'),
                    rec.get('districtname')
                ]
                # Filter out None, 'None', 'N/A' and join
                clean_locs = [l for l in loc_parts if l and l.lower() not in ['none', 'n/a', '']]
                location_str = ", ".join(clean_locs) if clean_locs else "Location Pending"

                txt += f"**📍 Location:** {location_str}\n"
                txt += f"**🏅 Status:** {level_str}\n\n"
                
                txt += f"**🏟️ Venue Details:**\n"
                txt += f"**Sport:** {sport}\n"
                if venue:
                    txt += f"**Venue:** {venue}\n"
                    txt += f"**Date:** {rec.get('match_date') or 'Check Schedule'}\n"
                else:
                    txt += "**Venue:** Not assigned yet.\n"
                    
                txt += f"\n**👤 Coach/Incharge:**\n"
                
                # HYBRID LOGIC: If SQL returns None for Incharge, ask RAG
                incharge_name = rec.get('cluster_incharge')
                incharge_contact = rec.get('incharge_mobile')
                
                if not incharge_name and rec.get('districtname'):
                    print("⚠️ Hybrid Trigger: SQL missing Incharge. Asking RAG...")
                    try:
                        rag_bot = get_or_init_rag_chain()
                        sport_detail = rec.get('sport_name') or rec.get('event_name') or "sports"
                        
                        # Use available hierarchy for RAG
                        rag_query = f"Who is the {sport_detail} incharge for "
                        if rec.get('mandalname'): rag_query += f"Mandal: {rec.get('mandalname')}, "
                        if rec.get('districtname'): rag_query += f"District: {rec.get('districtname')}?"
                        
                        rag_resp = rag_bot.invoke({"question": rag_query})
                        
                        # Extract simple text from chain response
                        rag_text = rag_resp.get('result', str(rag_resp)) if isinstance(rag_resp, dict) else str(rag_resp)
                        
                        # Filter out generic 'not found' messages to keep UI clean
                        if "couldn't find" in rag_text.lower() or "not available" in rag_text.lower():
                             txt += "**Status:** To be assigned by District Sports Officer.\n"
                        else:
                             txt += f"*(Retrieved via AI)*: {rag_text}\n"

                    except Exception as e:
                        print(f"Hybrid RAG Failed: {e}")
                        txt += "**Status:** Contact District Helpdesk.\n"
                else:
                    txt += f"**Name:** {incharge_name or 'N/A'}\n"
                    txt += f"**Contact:** {incharge_contact or 'N/A'}\n"
                
                
                final_response = {"response": txt, "source": "sql_database"}
                print(f"DEBUG RESPONSE ({ack_no}):\n{txt}")
                return final_response
             else:
                 # Fallthrough to RAG if not found? Or explicit error?
                 pass 


    # 2. Registration ID - REMOVED
    # Player lookup by Reg ID is disabled for privacy reasons.
    # Fallthrough to RAG/General Logic.


    # 3. Match/Fixture ID
    match_match = re.search(r'(?:match|fixture)\s*(?:id|no)?\s*[:#-]?\s*(\d+)', original_query, re.IGNORECASE)
    if match_match:
        fid = match_match.group(1)
        print(f"⚡ Intent: Fixture Lookup (ID: {fid})")
        try:
            res = get_fixture_details(fid)
            if res:
                txt = f"### 🏟️ Match Details (ID: {res['fixture_id']})\n"
                txt += f"**Match No:** {res['match_no']}\n"
                txt += f"**Venue:** {res['venue']}\n"
                txt += f"**Teams:** {res.get('team1_name', 'TBD')} vs {res.get('team2_name', 'TBD')}\n"
                txt += f"**Date:** {res['match_date']} ({res['match_day']}) @ {res['match_time']}\n"
                txt += f"**Round:** {res['round_name']}"
                return {"response": txt, "source": "sql_database"}
            else:
                 return {"response": f"❌ No match found with ID **{fid}**.", "source": "sql_database"}
        except Exception as e:
            print(f"SQL Error: {e}")

    # 4. Sport Schedule (New)
    # Supports "Schedule for Cricket" AND "Cricket Schedule"
    sport_pattern_1 = r'(?:schedule|events|matches)\s*(?:for|of|in)?\s*([a-zA-Z\s]+)'
    sport_pattern_2 = r'([a-zA-Z\s]+?)\s*(?:schedule|events|matches)'
    
    sport_match_objs = []
    m1 = re.search(sport_pattern_1, original_query, re.IGNORECASE)
    m2 = re.search(sport_pattern_2, original_query, re.IGNORECASE)
    
    # Prioritize "Schedule for Sport" if both somehow match, otherwise "Sport Schedule"
    sport_match = m1 if m1 else m2
    
    if sport_match:
        raw_sport = sport_match.group(1).strip()
        clean_sport = re.sub(r'\s+(matches|events|schedule|today|tomorrow)\b', '', raw_sport, flags=re.IGNORECASE).strip()
        if clean_sport.lower() not in ["the", "this"] and len(clean_sport) > 3:
             print(f"⚡ Intent: Sport Schedule ({clean_sport})")
             try:
                 schedules = get_sport_schedule(clean_sport)
                 if schedules:
                     txt = f"### 📅 {clean_sport.title()} Schedule (Next 5)\n"
                     for m in schedules[:5]:
                         txt += f"- **{m.get('event_name')}**: {m.get('team1_name')} vs {m.get('team2_name')} @ {m.get('venue')}\n"
                     return {"response": txt, "source": "sql_database"}
             except Exception as e:
                 print(f"SQL Error (Schedule): {e}")


    # 5. Geo Query
    NAME_REGEX = r"([a-zA-Z\s\-\(\)]+?)"
    geo_pattern_1 = fr"(?:district|mandal|village)\s*(?:does)?\s*{NAME_REGEX}\s*(?:belong|exist|register|in the db|in database)"
    geo_pattern_2 = fr"is\s+{NAME_REGEX}\s+a\s+(?:village|district|mandal)"
    geo_pattern_3 = fr"details\s*(?:for|about|of)?\s*{NAME_REGEX}"

    geo_match = re.search(geo_pattern_1, original_query, re.IGNORECASE)
    if not geo_match: geo_match = re.search(geo_pattern_2, original_query, re.IGNORECASE)
    if not geo_match: geo_match = re.search(geo_pattern_3, original_query, re.IGNORECASE)

    if geo_match:
        raw_name = geo_match.group(1).strip()
        clean_name = re.sub(r'\s+(district|mandal|village|zila|jilla)\b', '', raw_name, flags=re.IGNORECASE).strip()
        
        if len(clean_name) > 3 and clean_name.lower() not in ["the", "this", "that"]:
            print(f"⚡ Intent: Geo Lookup ({clean_name})")
            try:
                res = get_geo_details(clean_name)
                if res:
                    t = res['type']
                    d = res['data']
                    txt = f"### 📍 Location Found: {d.get('vill_nm') or d.get('mandal_nm') or d.get('dist_nm')}\n"
                    txt += f"**Type:** {t}\n"
                    if t == 'Village':
                        txt += f"**Mandal:** {d.get('parent_mandal')}\n"
                        txt += f"**District:** {d.get('parent_district')}"
                    elif t == 'Mandal':
                        txt += f"**District:** {d.get('parent_district')}"
                    return {"response": txt, "source": "sql_database"}
                else:
                    return {"response": f"🚫 **{clean_name}** could not be found in our Village/Mandal/District database.", "source": "sql_database"}
            except Exception as e:
                print(f"SQL Error: {e}")


    # 5.4 Level Schedule Lookup (Deterministic)
    schedule_pattern = r"(cluster|gp|gram\s*panchayat|mandal|ulb|district|state|assembly).*?(start|end|date|schedule|when|time)"
    schedule_match = re.search(schedule_pattern, original_query, re.IGNORECASE)
    if schedule_match:
        level_keyword = schedule_match.group(1).lower()
        print(f"⚡ Intent: Level Schedule Lookup (Level: {level_keyword})")
        
        # Hardcoded Schedule from 'CM_Cup_2025_RAG_Knowledge.txt'
        # This ensures 100% accuracy vs RAG hallucinations
        schedule_data = {
            "gram": "🗓️ **Grampanchayat Level:** 17 January to 22 January 2026 (6 days)",
            "gp": "🗓️ **Grampanchayat Level:** 17 January to 22 January 2026 (6 days)",
            "cluster": "🗓️ **Grampanchayat/Cluster Level:** 17 January to 22 January 2026 (6 days)",
            "mandal": "🗓️ **Mandal / ULB Level:** 28 January to 31 January 2026 (4 days)",
            "ulb": "🗓️ **Mandal / ULB Level:** 28 January to 31 January 2026 (4 days)",
            "assembly": "🗓️ **Assembly Constituency Level:** 03 February to 07 February 2026 (5 days)",
            "district": "🗓️ **District Level:** 10 February to 14 February 2026 (5 days)",
            "state": "🗓️ **State Level:** 19 February to 26 February 2026 (8 days)"
        }
        
        # Find best match
        response_txt = ""
        for key, val in schedule_data.items():
            if key in level_keyword:
                response_txt = val
                break
        
        if not response_txt:
            # Fallback for 'cluster' mapping if not caught above logic simple match
            if "cluster" in level_keyword: response_txt = schedule_data["cluster"]
            if "gram" in level_keyword: response_txt = schedule_data["gram"]
            if "mandal" in level_keyword: response_txt = schedule_data["mandal"]
            if "district" in level_keyword: response_txt = schedule_data["district"]
            if "state" in level_keyword: response_txt = schedule_data["state"]

        if response_txt:
             return {"response": f"{response_txt}\n\n*Note: Dates are subject to official guidelines.*", "source": "static_rule_engine"}

    # 5.5 Discipline/Level Lookup
    level_pattern = r"(disciplines?|sports?|games?|events?).*?\b(cluster|mandal|district|state)\b\s*(?:level)?"
    level_match = re.search(level_pattern, original_query, re.IGNORECASE)
    if level_match:
        level_name = level_match.group(2).lower()
        print(f"⚡ Intent: Discipline Lookup (Level: {level_name})")
        try:
            from rag.sql_queries import get_disciplines_by_level
            games = get_disciplines_by_level(level_name)
            if games:
                txt = f"### 🏅 Sports at {level_name.title()} Level\n"
                for g in games:
                    txt += f"- {g}\n"
                return {"response": txt, "source": "sql_database"}
            else:
                 # If SQL doesn't have data (e.g. new disciplines not in DB), Fallback to RAG
                 print(f"ℹ️ SQL found no disciplines for {level_name}. Falling back to RAG.")
                 pass 
        except Exception as e:
            print(f"SQL Error: {e}")
            pass

    # 6. Complex SQL Queries (Agentic)
    # Detects questions about counts, lists, specific aggregations (Agentic)
    # 1. Strong Rule Keywords (Age, Born, Criteria) - Trigger SQL immediately (handles typos like 'hokey')
    # 6. Complex SQL Queries (Agentic)
    # Detects questions about counts, lists, specific aggregations (Agentic)
    # 1. Strong Rule Keywords (Born, Birth) - Trigger SQL immediately
    # NOTE: Removed 'rules', 'age', 'limit' to let RAG handle them.
    if re.search(r"\b(born|birth)\b", original_query, re.IGNORECASE):
        print(f"🤖 Intent: Rule/Age Query (Triggering SQL Agent)")
        try:
             sql_response = run_sql_agent(original_query)
             if "I try to query" not in sql_response and "error" not in sql_response.lower():
                 return {"response": sql_response, "source": "sql_agent"}
        except Exception as e:
             print(f"SQL Agent Failed: {e}")

    # 2. General SQL Intents (Count, List, Who is) - Require a target object (player, sport, etc.)
    sql_intent_pattern = r"(how many|count|total|list|show|who is|what is|find).*(player|registration|venue|match|game|sport|cluster|incharge|hockey|cricket|kabaddi|kho|athletics|volleyball|ball|tennis|cycling|wrestling|karate|taekwondo|gymnastics|swimming|yoga|particip)"
    if re.search(sql_intent_pattern, original_query, re.IGNORECASE):
        print(f"🤖 Intent: Complex/Agentic SQL Query")
        try:
            sql_response = run_sql_agent(original_query)
            # if agent fails to understand, it might return a generic error.
            # We can check specific error strings if we want to fallback to RAG.
            if "I try to query" not in sql_response and "error" not in sql_response.lower():
                return {"response": sql_response, "source": "sql_agent"}
        except Exception as e:
            print(f"SQL Agent Failed: {e}")
            # Fallthrough to RAG if SQL agent fails
            pass

    # 7. RAG Fallback
    print(f"🧠 Intent: General Query")
    
    try:
        # Use Lazy Loaded Chain
        rag = get_or_init_rag_chain()
        if not rag:
             return {"response": "The AI Brain is initializing. Please try again in 10 seconds.", "source": "system"}
        
        # Memory Management
        # session_id passed in args
        chat_history = []
        if session_id:
            chat_history = CHAT_SESSIONS.get(session_id, [])
        
        # Invoke Chain with History
        input_payload = {"question": original_query, "chat_history": chat_history}
        
        # rag.invoke now expects a dict because we updated chain.py
        response_data = rag.invoke(input_payload)
        
        # response_data is a dictionary from ask_llm {"response", "model_used"}
        if isinstance(response_data, dict):
            final_answer = response_data.get("response", "No response")
            model = response_data.get("model_used", "rag")
        else:
             final_answer = str(response_data)
             model = "rag"

        # Update Memory
        if session_id:
            # Append turn: (User, AI)
            chat_history.append(("User", original_query))
            chat_history.append(("AI", final_answer))
            # Keep last 10 turns (20 items)
            CHAT_SESSIONS[session_id] = chat_history[-20:]

        return {"response": final_answer, "source": "rag_knowledge_base", "model_used": model}
    except Exception as e:
        print(f"RAG Crash: {e}")
        return {"response": f"I encountered an error accessing the knowledge base. Error: {str(e)}", "source": "error_handler"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Auto-generate session_id if missing to support tools like Postman
    # However, the client MUST send this back to maintain state!
    current_session_id = request.session_id or str(uuid.uuid4())
    
    response_data = await process_user_query(request.query, current_session_id)
    
    # Inject session_id into response so client knows what to send back
    if isinstance(response_data, dict):
        response_data["session_id"] = current_session_id
        
    return response_data

@app.post("/ask")
async def ask_endpoint(request: ChatRequest):
    return await process_user_query(request.query, request.session_id)

# --------------------------------------------------
# 9. WhatsApp Endpoint
# --------------------------------------------------
@app.post("/whatsappchat")
async def whatsapp_chat_endpoint(request: WhatsAppChatRequest):
    """
    WhatsApp specialized endpoint.
    Uses 'phone_number' as session_id for continuity.
    """
    user_message = (request.user_message or "").strip()
    session_id = request.phone_number  # Use phone number as persistent session ID

    if not user_message:
        raise HTTPException(status_code=400, detail="user_message cannot be empty")

    try:
        # Call the unified logic
        return await process_user_query(user_message, session_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing Error: {str(e)}")
