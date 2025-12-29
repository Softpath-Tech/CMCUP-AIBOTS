import sys
import os
import re
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
from rag.sql_queries import get_fixture_details, get_geo_details, get_sport_schedule
# Also importing get_player_by_phone from lookup (which uses SQL now)
from rag.lookup import get_player_by_phone, get_player_by_reg_id

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

class WhatsAppChatRequest(BaseModel):
    user_message: str
    first_name: Optional[str] = None
    phone_number: Optional[str] = None

# Global RAG Cache (Lazy Loaded)
rag_chain = None

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
# 6. Helpers
# --------------------------------------------------
def extract_plain_text(resp) -> str:
    """Try to extract a single answer string from various response shapes."""
    if resp is None:
        return ""
    if isinstance(resp, (str, int, float)):
        return str(resp)
    if isinstance(resp, dict):
        return _extract_from_dict(resp)
    if isinstance(resp, (list, tuple)):
        return _extract_from_list(resp)
    return str(resp)

def _extract_from_dict(d: dict) -> str:
    # Preferred scalar keys
    for key in ("response", "answer", "text", "content", "message", "output", "result"):
        v = d.get(key)
        if isinstance(v, (str, int, float)):
            return str(v)
    for key in ("choices", "outputs", "results"):
        if key in d:
            return extract_plain_text(d[key])
    for v in d.values():
        candidate = extract_plain_text(v)
        if candidate:
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
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    The Hybrid Intent Router 2.1:
    1. Static Data (CM, Helpdesk) -> Instant
    2. Phone -> SQL
    3. Reg ID -> SQL
    4. Match ID -> SQL 
    5. Geo Query -> SQL 
    6. Sport Schedule -> SQL (New)
    7. RAG Fallback
    """
    user_query = request.query.strip().lower() # Normalize Lower
    
    # 0. Static Data Interceptor
    STATIC_KNOWLEDGE = {
        "cm": "The Hon'ble Chief Minister of Telangana is **Sri A. Revanth Reddy**.",
        "minister": "The Hon'ble Chief Minister of Telangana and Sports Minister is **Sri A. Revanth Reddy**.",
        "helpdesk": "📞 **Helpdesk Support:**\n\nFor queries, please contact: **040-23232323** or email: **helpdesk@cmcup.in**",
        "weather": "🌦️ **Weather:** For real-time weather updates, please check your local news. Matches proceed unless severe rain occurs.",
        "pension": "💰 **Pension Schemes:**\n\nRetired players who have represented the state/nation are eligible for monthly pensions. Please visit **sports.telangana.gov.in** for application details.",
        "stadium": "🏟️ **Main Venue:**\n\nThe opening ceremony and main events are held at **Gachibowli Indoor Stadium, Hyderabad**.",
        "vision": "🎯 **Vision 2025:**\n\nTo identify rural talent and nurture them into world-class athletes for the upcoming Olympics and National Games.",
        "budget": "💰 **Sports Budget:**\n\nThe government has allocated **₹500 Crores** for sports infrastructure development in this fiscal year.",
        "infrastructure": "🏗️ **Infrastructure:**\n\nState-of-the-art sports complexes are being developed in every district HQ.",
        "award": "🏆 **Cash Awards:**\n\n- Olympic Gold: **₹2 Cr**\n- Silver: **₹1 Cr**\n- Bronze: **₹50 Lakhs**",
        "quota": "📜 **Sports Quota:**\n\n**2% reservation** is provided for meritorious sports persons in government jobs and education.",
        "opening": "🎉 **Opening Ceremony:**\n\nThe Grand Opening Ceremony will be held at **Gachibowli Stadium** on **Jan 26th**."
    }
    
    for key, response in STATIC_KNOWLEDGE.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, user_query): 
             print(f"⚡ Intent: Static Data ({key})")
             return {"response": response, "source": "static_knowledge"}
             
    # 0.5 Participation Stats (New)
    if any(k in user_query for k in ["total participation", "how many players", "total registration", "total players", "no participation"]):
        from rag.sql_queries import get_participation_stats
        count = get_participation_stats()
        return {
            "response": f"📊 **Participation Status:**\n\nA total of **{count} players** have registered for the Chief Minister's Cup (CM Cup) 2025 so far!",
            "model_used": "sql_database"
        }

    # 1. Phone Number match
    original_query = request.query.strip() # Keep casing for Reg IDs if needed
    phone_match = re.search(r'\b\d{10}\b', original_query)
    if phone_match:
        phone_number = phone_match.group(0)
        print(f"⚡ Intent: Player Lookup (Phone: {phone_number})")
        try:
            answer = get_player_by_phone(phone_number)
            return {"response": answer, "source": "sql_database"}
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    # 2. Registration ID
    reg_id_match = re.search(r'\b[A-Za-z0-9-]*\d[A-Za-z0-9-]*\b', original_query)
    if reg_id_match:
        potential_id = reg_id_match.group(0)
        if 5 <= len(potential_id) <= 25 and not "match" in potential_id.lower():
             try:
                lookup_res = get_player_by_reg_id(potential_id)
                if "Record(s)" in lookup_res:
                     print(f"⚡ Intent: Reg ID Lookup ({potential_id})")
                     return {"response": lookup_res, "source": "sql_database"}
             except: pass

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
    sport_pattern = r'(?:schedule|events|matches)\s*(?:for|of|in)?\s*([a-zA-Z\s]+)'
    sport_match = re.search(sport_pattern, original_query, re.IGNORECASE)
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

    # 5.5 Discipline/Level Lookup
    level_pattern = r"(disciplines|sports|games).*?(cluster|mandal|district|state)\s*(?:level)?"
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
                 return {"response": f"ℹ️ No specific disciplines found listed for **{level_name}** level.", "source": "sql_database"}
        except Exception as e:
            print(f"SQL Error: {e}")

    # 6. RAG Fallback
    print(f"🧠 Intent: General Query")
    
    try:
        # Use Lazy Loaded Chain
        rag = get_or_init_rag_chain()
        if not rag:
             return {"response": "The AI Brain is initializing. Please try again in 10 seconds.", "source": "system"}
        
        response_text = rag.invoke(original_query)
        return {"response": response_text, "source": "rag_knowledge_base"}
    except Exception as e:
        print(f"RAG Crash: {e}")
        return {"response": "I encountered an error accessing the knowledge base. Please contact helpdesk.", "source": "error_handler"}

@app.post("/ask")
async def ask_endpoint(request: ChatRequest):
    return await chat_endpoint(request)

# --------------------------------------------------
# 9. WhatsApp Endpoint
# --------------------------------------------------
@app.post("/whatsappchat")
async def whatsapp_chat_endpoint(request: WhatsAppChatRequest):
    """
    WhatsApp specialized endpoint: accepts JSON with user_message.
    """
    user_message = (request.user_message or "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="user_message cannot be empty")

    try:
        rag = get_or_init_rag_chain()
        response_text = rag.invoke(user_message)
        plain = extract_plain_text(response_text)
        return Response(content=plain, media_type="text/plain")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")
