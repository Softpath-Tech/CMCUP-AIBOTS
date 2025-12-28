import sys
import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# 1. Ensure Python can find your 'rag' folder
sys.path.append(os.getcwd())

# 2. Import your existing Brains
from rag.chain import get_rag_chain
from rag.lookup import get_player_by_phone  # Ensure you created this file based on previous steps

# 3. Initialize App
app = FastAPI(
    title="SATG Sports Chatbot API",
    description="Hybrid RAG + SQL Engine for Player Stats & Rules",
    version="1.0.0"
)

# 4. CORS Setup (Allows Frontend/Mobile to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Define Data Model (Input Format)
class ChatRequest(BaseModel):
    query: str

# 6. Global Variables for Caching Brains
rag_chain = None

@app.on_event("startup")
async def startup_event():
    """Load the RAG Brain once when server starts (Faster responses)"""
    global rag_chain
    print("🚀 Server Starting... Loading RAG Chain...")
    try:
        rag_chain = get_rag_chain()
        print("✅ RAG Chain Loaded Successfully!")
    except Exception as e:
        print(f"❌ Error loading RAG Chain: {e}")

@app.get("/")
def read_root():
    return {"status": "online", "message": "SATG Chatbot Engine is Running 🚀"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    The Hybrid Router:
    - If Phone Number detected -> Lookup SQL
    - Else -> Search RAG Vector DB
    """
    user_query = request.query.strip()
    
    # --- LOGIC LAYER ---
    
    # 1. Check for Phone Number (10 digits)
    phone_match = re.search(r'\b\d{10}\b', user_query)
    
    if phone_match:
        phone_number = phone_match.group(0)
        print(f"⚡ Intent: Player Lookup (Phone: {phone_number})")
        
        # Call your SQL Lookup Tool
        try:
            # Note: Ensure get_player_by_phone returns a string
            answer = get_player_by_phone(phone_number)
            return {"response": answer, "source": "sql_database"}
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    # 2. If no phone, use RAG (General Query)
    else:
        print(f"🧠 Intent: General Query")
        if not rag_chain:
            raise HTTPException(status_code=503, detail="RAG Brain not initialized yet.")
        
        try:
            # Invoke Gemini + Qdrant
            response_text = rag_chain.invoke(user_query)
            return {"response": response_text, "source": "rag_knowledge_base"}
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")
