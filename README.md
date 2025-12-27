# 🤖 CMCUP-AIBOTS: Hybrid RAG Chatbot

This project is an advanced AI Chatbot designed for the **CM Cup Sports Tournament**.
It uses a **Hybrid Strategy** to provide accurate answers:
1.  **Direct Lookup:** For sensitive or high-change data (Player Status, Scores) using exact matching.
2.  **RAG (Retrieval-Augmented Generation):** For general knowledge (Fixtures, Districts, Rules) using Semantic Search + LLM.

---

## 🏗️ Architecture

### 1. The Direct Lookup System (Privacy & Accuracy)
*   **Trigger:** Detects valid **10-digit Mobile Numbers**.
*   **Data Source:** `data/csvs/player_details.csv`, `tb_selected_players.csv`, `tb_player_results.csv`.
*   **Mechanism:** Direct Pandas search. Bypass Vector DB.
*   **Output:** Precise "Player Status Card" with Name, Reg ID, Level (Mapped), Status, and Score.

### 2. The RAG System (General Knowledge)
*   **Trigger:** Any query NOT containing a phone number.
*   **Data Source:** 7 General CSVs (`districtmaster`, `tb_fixtures`, `tb_events`, etc.).
*   **Pipeline:**
    1.  **CSV → Text:** `process_sql_data.py` converts rows into narrative Markdown.
    2.  **Ingestion:** `ingestion/run_ingestion.py` chunks and embeds text.
    3.  **Vector Store:** **Qdrant** stores embeddings (using `text-embedding-004`).
    4.  **LLM:** **Gemini 2.0 Flash Experimental** answers based on retrieved context.

---

## 📂 Project Structure

```plaintext
rag-chatbot/
│
├── api/
│   └── main.py             # FastAPI App (Routes user queries)
│
├── data/
│   ├── csvs/               # Raw Input Data (10 Tables)
│   ├── mdFiles/            # Generated Narrative Data for RAG
│   └── qdrant_db/          # Vector Database Storage
│
├── ingestion/
│   ├── run_ingestion.py    # Embeds mdFiles -> Qdrant
│   └── embed_store.py      # Embedding Logic
│
├── rag/
│   ├── lookup.py           # Logic for Player CSV Search
│   ├── chain.py            # RAG Chain setup (Gemini 2.0)
│   └── retriever.py        # Qdrant Retriever
│
├── process_sql_data.py     # Script to convert CSV -> Markdown
└── requirements.txt        # Dependencies
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
*   Python 3.10+
*   A **Google Gemini API Key** (Free Tier is fine).

### 2. Installation
```bash
# Clone Repository
git clone <repo-url>
cd rag-chatbot

# Install Dependencies
pip install -r requirements.txt
```

### 3. Environment Config
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
*Note: This single key powers both the Chat Model (`gemini-2.0-flash-exp`) and Embeddings (`text-embedding-004`).*

---

## 🚀 Usage Guide

### A. Initialize Data (First Run)
If you have new CSV data:
1.  **Convert Data:**
    ```bash
    python process_sql_data.py
    ```
    *Generates MD files in `data/mdFiles`.*

2.  **Ingest to Brain:**
    ```bash
    python ingestion/run_ingestion.py
    ```
    *Creates/Updates the Qdrant Vector Store.*

### B. Run the Chatbot API
Start the server:
```bash
uvicorn api.main:app --reload
```
*Server runs at: `http://127.0.0.1:8000`*

### C. Test the Bot
**Endpoint:** `POST /ask`

**Example 1: Player Lookup**
```json
{
  "question": "Status for 7416613302"
}
```
*Result:* Returns detailed Player Card (Name, ID, Level, Score).

**Example 2: General RAG**
```json
{
  "question": "Tell me about the match schedule for Fixture 1"
}
```
*Result:* Returns AI-generated answer based on stored knowledge.

---

## ⚠️ Known Issues
*   **Google API Quota:** The Free Tier has rate limits. If you see `429 Resource Exhausted`, wait 60 seconds or upgrade the key.
    *   *Note:* Player Lookup does NOT use the API, so it always works!

---

**Built with:** LangChain 🦜🔗, Qdrant 🧠, and Google Gemini ✨.