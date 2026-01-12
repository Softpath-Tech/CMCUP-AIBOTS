"""
Configuration settings for the RAG Chatbot application.
Centralizes magic numbers and configuration values.
"""

# RAG Configuration
RAG_CHUNK_SIZE = 1000
RAG_CHUNK_OVERLAP = 200
RAG_SEARCH_K = 10  # Number of chunks to retrieve
RAG_CHAT_HISTORY_LIMIT = 20  # Keep last 20 items (10 turns)

# LLM Configuration
PRIMARY_MODEL = "gemini-2.5-flash"
SECONDARY_MODEL = "gpt-4o"  # Fallback model

# Embedding Configuration
# Note: Ingestion uses OpenAI (1536 dims), Retriever uses Gemini (768 dims)
# Different collections are used: rag_knowledge_base vs rag_knowledge_base_gemini
INGESTION_EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI
INGESTION_EMBEDDING_DIMS = 1536
RETRIEVER_EMBEDDING_MODEL = "models/embedding-001"  # Gemini
RETRIEVER_EMBEDDING_DIMS = 768

# Database Configuration
DB_CSV_DIR = "data/csvs"
QDRANT_DB_PATH = "data/qdrant_db"
QDRANT_COLLECTION_OPENAI = "rag_knowledge_base"
QDRANT_COLLECTION_GEMINI = "rag_knowledge_base_gemini"

# Session Configuration
SESSION_TIMEOUT_SECONDS = 3600  # 1 hour

# API Configuration
MAX_QUERY_LENGTH = 1000
MAX_RESPONSE_LENGTH = 5000
