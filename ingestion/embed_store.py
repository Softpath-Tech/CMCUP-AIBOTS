from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Qdrant
from config.settings import QDRANT_URL, QDRANT_COLLECTION


def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"
    )


def store_chunks(chunks):
    embeddings = get_embedding_model()

    qdrant = Qdrant.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION
    )

    return qdrant
