from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_retriever():
    # MUST MATCH THE MODEL USED IN INGESTION!
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    client = QdrantClient(path="data/qdrant_db")
    
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="rag_knowledge_base",
        embedding=embeddings,
    )
    
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )