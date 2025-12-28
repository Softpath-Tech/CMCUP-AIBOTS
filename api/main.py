import sys
import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --------------------------------------------------
# 1. Ensure Python can find project root (Render-safe)
# --------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# --------------------------------------------------
# 2. Import RAG & SQL logic
# --------------------------------------------------
from rag.chain import get_rag_chain
from rag.lookup import get_player_by_phone

# --------------------------------------------------
# 3. Initialize FastAPI App
# --------------------------------------------------
app = FastAPI(
    title="SATG Sports Chatbot API",
    description="Hybrid RAG + SQL Engine for Player Stats & Rules",
    version="1.0.0"
)

# --------------------------------------------------
# 4. Enable CORS (Open for demo)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# 5. Request Model
# --------------------------------------------------
class ChatRequest(BaseModel):
    query: str

# --------------------------------------------------
# 6. Global RAG Cache (Lazy Loaded)
# --------------------------------------------------
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
# 7. Health Check (IMPORTANT for Render)
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# 8. Root Endpoint
# --------------------------------------------------
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "SATG Chatbot Engine is Running 🚀"
    }


# --------------------------------------------------
# 9. Chat Endpoint (Hybrid Router)
# --------------------------------------------------
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Hybrid Query Router:
    - Detects phone number → SQL lookup
    - Else → RAG (Vector DB + LLM)
    """

    user_query = request.query.strip()

    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # ----------------------------------------------
    # Phone Number Detection (10 digits)
    # ----------------------------------------------
    phone_match = re.search(r"\b\d{10}\b", user_query)

    if phone_match:
        phone_number = phone_match.group(0)
        print(f"⚡ Intent: Player Lookup | Phone: {phone_number}")

        try:
            result = get_player_by_phone(phone_number)
            return {
                "response": result,
                "source": "sql_database"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database Error: {str(e)}"
            )

    # ----------------------------------------------
    # RAG Path (General Query)
    # ----------------------------------------------
    print("🧠 Intent: RAG Query")

    try:
        rag = get_or_init_rag_chain()
        response_text = rag.invoke(user_query)

        return {
            "response": response_text,
            "source": "rag_knowledge_base"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"RAG Error: {str(e)}"
        )
