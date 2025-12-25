from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_retriever():
    # MUST MATCH THE MODEL USED IN INGESTION!
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    client = QdrantClient(path="data/qdrant_db")
    
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="rag_knowledge_base",
        embedding=embeddings,
    )
    
    return vector_store.as_retriever(search_kwargs={"k": 3})