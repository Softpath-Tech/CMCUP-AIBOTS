# rag_engine.py

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost", port=6333)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "cmc_rag"


def query_rag(query: str, menu_path: str):
    vector = embedder.encode(query).tolist()

    results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=5,
        query_filter={
            "must": [{"key": "menu_path", "match": {"value": menu_path}}]
        }
    )

    if not results:
        return "No relevant information found."

    return "\n".join(r.payload["text"] for r in results)
