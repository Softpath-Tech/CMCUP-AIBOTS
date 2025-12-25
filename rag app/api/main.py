from fastapi import FastAPI
from pydantic import BaseModel
from rag.chain import get_rag_chain

app = FastAPI(title="RAG Chatbot API")

qa_chain = get_rag_chain()


class QueryRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_question(request: QueryRequest):
    answer = qa_chain.run(request.question)
    return {"answer": answer}
