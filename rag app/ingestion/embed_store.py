import os
import time
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

load_dotenv()

def create_vector_store(chunks):
    print("🧠 Initializing Embeddings & Vector Store...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ CRITICAL ERROR: GOOGLE_API_KEY is missing!")
        return

    # 1. SWITCH TO NEWER MODEL (Often helps with Quota)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # 2. Setup Qdrant Client
    client = QdrantClient(path="data/qdrant_db")
    collection_name = "rag_knowledge_base"

    # 3. Create Collection if missing
    if not client.collection_exists(collection_name):
        print(f"📦 Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    print(f"🚀 Preparing to ingest {len(chunks)} chunks...")

    # 4. ROBUST INIT: Catch the "Dummy Text" 429 Error
    vector_store = None
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # This line sends "dummy_text" to Google to check dimensions
            vector_store = QdrantVectorStore(
                client=client,
                collection_name=collection_name,
                embedding=embeddings,
            )
            break # If successful, exit loop
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait_time = 45 # Wait 45 seconds as requested by API
                print(f"⚠️  Rate Limit hit on startup (Attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e # If it's another error, crash so we can see it

    if not vector_store:
        print("❌ Failed to initialize after retries. Please wait 2 minutes and try again.")
        return

    # 5. Add Documents
    try:
        vector_store.add_documents(documents=chunks)
        print("✅ SUCCESS: Data embedded successfully!")
    except Exception as e:
        print(f"❌ Error adding documents: {e}")

    return vector_store