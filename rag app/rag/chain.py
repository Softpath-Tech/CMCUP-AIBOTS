from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from rag.retriever import get_retriever
from dotenv import load_dotenv

load_dotenv()

def get_rag_chain():
    # 1. Setup Brain (Using Gemini 2.0 Flash Experimental)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # <--- UPDATED to 2.0 Flash
        temperature=0.2
    )

    # 2. Setup Memory
    retriever = get_retriever()

    # 3. Create Prompt
    template = """You are a helpful assistant for the Sports Authority of Telangana (SATG).
    Answer the question based ONLY on the following context.
    If you don't know the answer, say "I don't have that information."

    Context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 4. Build Chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain