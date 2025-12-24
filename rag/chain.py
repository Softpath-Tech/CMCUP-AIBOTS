from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from rag.retriever import get_retriever


def get_rag_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )

    retriever = get_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )

    return qa_chain
