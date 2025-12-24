from langchain_community.vectorstores import Qdrant
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import QDRANT_URL, QDRANT_COLLECTION


def get_retriever(k: int = 4):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"
    )

    db = Qdrant(
        url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings
    )

    return db.as_retriever(search_kwargs={"k": k})
