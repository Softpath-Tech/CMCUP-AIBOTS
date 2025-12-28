import sys
import os
import re
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
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


class WhatsAppChatRequest(BaseModel):
    user_message: str
    first_name: Optional[str] = None
    phone_number: Optional[str] = None

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


def extract_plain_text(resp) -> str:
    """Try to extract a single answer string from various response shapes.

    Handles:
    - plain strings
    - dicts with common keys like 'response', 'answer', 'text', 'content'
    - nested dicts/lists (recurses)
    - lists (returns first non-empty string item)
    Falls back to str(resp) if nothing better found.
    """
    # Delegate to small top-level helpers to keep this function simple.
    if resp is None:
        return ""

    if isinstance(resp, (str, int, float)):
        return str(resp)

    if isinstance(resp, dict):
        return _extract_from_dict(resp)

    if isinstance(resp, (list, tuple)):
        return _extract_from_list(resp)

    try:
        return str(resp)
    except Exception:
        return ""


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


# --------------------------------------------------
# WhatsApp Chat Endpoint
# --------------------------------------------------
@app.post("/whatsappchat")
async def whatsapp_chat_endpoint(request: WhatsAppChatRequest):
    """
    Accepts a JSON body with:
    {
      "user_message": "...",
      "first_name": "...",
      "phone_number": "..."
    }

    Behavior:
    - If phone_number is provided (non-empty) -> call SQL lookup via get_player_by_phone
      and return the result as plain text.
    - Else -> send user_message to RAG chain and return the generated text as plain text.
    """

    # Use `user_message` as the query source. `phone_number` is intentionally ignored per request.
    user_message = (request.user_message or "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="user_message cannot be empty")

    try:
        rag = get_or_init_rag_chain()
        response_text = rag.invoke(user_message)
        # Return plain text only
        return Response(content=str(response_text), media_type="text/plain")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")
