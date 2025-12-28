from fastapi import FastAPI
from pydantic import BaseModel
from rag.chain import get_rag_chain

app = FastAPI(title="RAG Chatbot API")

try:
    qa_chain = get_rag_chain()
except Exception as e:
    print(f"⚠️ Warning: RAG Chain could not be loaded: {e}")
    qa_chain = None


class QueryRequest(BaseModel):
    question: str


import re
from rag.lookup import get_player_status

@app.post("/ask")
def ask_question(request: QueryRequest):
    # 1. Direct Lookup Strategy: Check for Mobile Number (10 digits)
    phone_match = re.search(r'\b\d{10}\b', request.question)
    
    if phone_match:
        phone_number = phone_match.group(0)
        print(f"🔢 Detected Phone Number: {phone_number} -> Using Lookup Tool")
        # Direct Call to Lookup Logic
        answer = get_player_status(phone_number)
        return {"response": answer, "model_used": "Direct Lookup"}

    # 2. RAG Strategy: General Questions
    print("🧠 No ID found -> Using RAG Vector Store")
    if qa_chain:
        try:
            # qa_chain now returns {"response": str, "model_used": str}
            result = qa_chain.invoke(request.question)
            return result
        except Exception as e:
            return {"response": f"I'm encountering an issue accessing my knowledge base correct: {e}", "model_used": "Error"}
    else:
        return {"response": "I am currently unable to answer general questions (RAG System unavailable).", "model_used": "None"}
