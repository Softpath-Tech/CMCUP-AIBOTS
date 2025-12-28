import sys
import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. Ensure Python can find your 'rag' folder
sys.path.append(os.getcwd())

# 2. Import Brains & Data Store
from rag.chain import get_rag_chain
from rag.sql_queries import get_fixture_details, get_geo_details, get_sport_schedule

# 3. Initialize App
app = FastAPI(
    title="SATG Sports Chatbot API",
    description="Hybrid RAG + SQL Engine for Player Stats & Rules",
    version="1.1.0"
)

app.mount("/demo", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

rag_chain = None

@app.on_event("startup")
async def startup_event():
    """Load the RAG Brain and SQL Store once when server starts."""
    global rag_chain
    print("🚀 Server Starting... Loading RAG Chain & Data Store...")
    
    # 1. Init RAG
    try:
        rag_chain = get_rag_chain()
        print("✅ RAG Chain Loaded Successfully!")
    except Exception as e:
        print(f"❌ Error loading RAG Chain: {e}")

    # 2. Init SQL DataStore
    try:
        ds = get_datastore()
        ds.init_db()
    except Exception as e:
        print(f"❌ Error loading DataStore: {e}")

@app.get("/")
def read_root():
    return {"status": "online", "message": "SATG Chatbot Engine is Running 🚀"}

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
    # Hardcoded for 100% reliability on common questions
    STATIC_KNOWLEDGE = {
        "cm": "The Hon'ble Chief Minister of Telangana is **Sri A. Revanth Reddy**.",
        "minister": "The Hon'ble Chief Minister of Telangana and Sports Minister is **Sri A. Revanth Reddy**.",
        "helpdesk": "📞 **Helpdesk Support:**\n\nFor queries, please contact: **040-23232323** or email: **helpdesk@cmcup.in**",
        "contact": "📞 **Helpdesk Support:**\n\nFor queries, please contact: **040-23232323** or email: **helpdesk@cmcup.in**",
        "weather": "🌦️ **Weather:** For real-time weather updates, please check your local news. Matches proceed unless severe rain occurs.",
        "pension": "💰 **Pension Schemes:**\n\nRetired players who have represented the state/nation are eligible for monthly pensions. Please visit **sports.telangana.gov.in** for application details.",
        "stadium": "🏟️ **Main Venue:**\n\nThe opening ceremony and main events are held at **Gachibowli Indoor Stadium, Hyderabad**.",
        "vision": "🎯 **Vision 2025:**\n\nTo identify rural talent and nurture them into world-class athletes for the upcoming Olympics and National Games.",
        "budget": "💰 **Sports Budget:**\n\nThe government has allocated **₹500 Crores** for sports infrastructure development in this fiscal year.",
        "infrastructure": "💰 **Sports Budget:**\n\nThe government has allocated **₹500 Crores** for sports infrastructure development in this fiscal year.",
        "award": "🏆 **Cash Awards:**\n\n- Olympic Gold: **₹2 Cr**\n- Silver: **₹1 Cr**\n- Bronze: **₹50 Lakhs**",
        "gold": "🏆 **Cash Awards:**\n\n- Olympic Gold: **₹2 Cr**\n- Silver: **₹1 Cr**\n- Bronze: **₹50 Lakhs**",
        "quota": "📜 **Sports Quota:**\n\n**2% reservation** is provided for meritorious sports persons in government jobs and education.",
        "reservation": "📜 **Sports Quota:**\n\n**2% reservation** is provided for meritorious sports persons in government jobs and education.",
        "cluster": "📍 **Cluster Info:**\n\nClusters are groups of villages for local administration. Please provide your **Village Name** to find your specific Cluster.",
        "opening": "🎉 **Opening Ceremony:**\n\nThe Grand Opening Ceremony will be held at **Gachibowli Stadium** on **Jan 26th**."
    }
    
    # Keyword search for static data
    for key, response in STATIC_KNOWLEDGE.items():
        if key in user_query and len(user_query) < 50: # Short queries only
             print(f"⚡ Intent: Static Data ({key})")
             return {"response": response, "source": "static_knowledge"}

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
    # "List events for Wrestling", "Schedule for Kabaddi", "Basketball matches today"
    # Capture "Wrestling", "Kabaddi", "Basketball" but ignore "matches today"
    
    # Regex Strategy: Capture everything after key phrase, then clean it.
    sport_pattern = r'(?:schedule|events|matches)\s*(?:for|of|in)?\s*([a-zA-Z\s]+)'
    sport_match = re.search(sport_pattern, original_query, re.IGNORECASE)
    if sport_match:
        # e.g. "Basketball matches today" -> "Basketball matches today"
        raw_sport = sport_match.group(1).strip()
        
        # Clean specific suffixes common in natural phrasing
        clean_sport = re.sub(r'\s+(matches|events|schedule|today|tomorrow)\b', '', raw_sport, flags=re.IGNORECASE).strip()
        
        # Filter out stopwords
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
        # Clean suffixes
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

    # 6. RAG Fallback
    print(f"🧠 Intent: General Query")
    
    if not rag_chain:
        # Fallback to simple static response if RAG is dead
        return {"response": "The AI Brain is initializing. Please try again in 10 seconds.", "source": "system"}

    try:
        response_text = rag_chain.invoke(original_query)
        return {"response": response_text, "source": "rag_knowledge_base"}
    except Exception as e:
        # Fail gracefully
        print(f"RAG Crash: {e}")
        return {"response": "I encountered an error accessing the knowledge base. Please contact helpdesk.", "source": "error_handler"}

@app.post("/ask")
async def ask_endpoint(request: ChatRequest):
    return await chat_endpoint(request)
