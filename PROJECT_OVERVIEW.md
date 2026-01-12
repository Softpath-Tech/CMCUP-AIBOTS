# 📋 Complete Project Overview: CM Cup RAG Chatbot

## 🎯 Project Purpose

This is a **Multilingual Hybrid RAG (Retrieval-Augmented Generation) Chatbot** built for the **CM Cup Sports Tournament** organized by the Sports Authority of Telangana (SATG). The system provides intelligent, context-aware answers in **English, Hindi, and Telugu** for players, parents, coaches, and officials.

---

## 🏗️ System Architecture

### **Three-Layer Intelligence System**

#### 1. **Direct Lookup Layer** (High Precision)
- **Trigger**: Detects 10-digit mobile numbers or acknowledgment numbers
- **Source**: SQLite database loaded from CSV files (`data/csvs/`)
- **Action**: Bypasses LLM to fetch exact player records
- **Result**: Deterministic player status cards with zero hallucinations
- **Key Functions**: `get_player_venues_by_phone()`, `get_player_venue_by_ack()`

#### 2. **SQL Query Layer** (Structured Data)
- **Purpose**: Handles structured queries about schedules, venues, disciplines, officers
- **Database**: In-memory SQLite database (loaded from CSVs at startup)
- **Key Functions**:
  - `get_sport_schedule()` - Match schedules by sport
  - `get_disciplines_by_level()` - Sports available at each level
  - `get_geo_details()` - Village/Mandal/District lookups
  - `get_fixture_details()` - Match details by ID
  - `get_sport_rules()` - Age criteria and eligibility
- **SQL Agent**: `run_sql_agent()` - LLM-powered text-to-SQL for complex queries

#### 3. **RAG Layer** (Knowledge Base)
- **Purpose**: Answers general questions about rules, regulations, tournament info
- **Pipeline**:
  1. **Ingestion**: Markdown files → Chunks → Embeddings → Qdrant Vector DB
  2. **Retrieval**: Semantic search using Gemini embeddings (768 dimensions)
  3. **Generation**: LLM (Gemini 2.5 Flash / GPT-5.2 Pro) synthesizes answers
- **Vector DB**: Qdrant (local storage at `data/qdrant_db/`)
- **Collection**: `rag_knowledge_base_gemini`

---

## 📂 Project Structure

```
rag-chatbot/
├── api/
│   └── main.py                    # FastAPI application & routing
│
├── config/
│   └── settings.py               # Configuration (currently empty)
│
├── data/
│   ├── csvs/                     # Raw source data (CSVs)
│   │   ├── player_details.csv
│   │   ├── tb_fixtures.csv
│   │   ├── tb_discipline.csv
│   │   ├── districtmaster.csv
│   │   ├── mandalmaster.csv
│   │   ├── villagemaster.csv
│   │   └── ... (14 CSV files)
│   │
│   ├── mdFiles/                   # Processed knowledge base (Markdown)
│   │   └── [12 markdown files]
│   │
│   ├── new data/                  # Additional data sources
│   │   ├── DistrictWIseClusters.xlsx
│   │   ├── MEO_Details.xlsx
│   │   ├── district_officers.csv
│   │   └── Mandal_Incharges_Cleaned.txt
│   │
│   └── qdrant_db/                 # Local Vector Database
│
├── ingestion/
│   ├── run_ingestion.py          # Main ingestion script
│   ├── chunking.py               # Document chunking logic
│   ├── embed_store.py            # Embedding & storage (OpenAI embeddings)
│   └── load_pdf.py               # PDF loading utilities
│
├── rag/
│   ├── chain.py                  # RAG pipeline & LiteLLM config
│   ├── retriever.py              # Qdrant retriever configuration
│   ├── llm_manager.py            # LLM orchestration (Gemini/OpenAI)
│   ├── data_store.py             # SQLite in-memory database wrapper
│   ├── sql_queries.py            # Predefined SQL query functions
│   ├── sql_agent.py              # Text-to-SQL agent
│   ├── location_search.py        # Officer/cluster/mandal search
│   └── translations.py            # Multilingual menu translations
│
├── tests/                         # Test suites
│
├── api/main.py                    # Main FastAPI entry point
├── requirements.txt               # Python dependencies
├── render.yaml                   # Render deployment config
├── start.sh                      # Deployment startup script
└── README.md                     # Project documentation
```

---

## 🔄 Request Flow

### **User Query Processing** (`api/main.py` → `process_user_query()`)

1. **Menu State Machine** (Interactive Navigation)
   - Handles menu navigation (Main Menu → Sub-menus)
   - Manages session state (`SESSION_STATE`, `SESSION_DATA`)
   - Supports multilingual menus (English, Telugu, Hindi)

2. **Intent Detection & Routing**
   - **Phone Number** → Direct SQL lookup
   - **Acknowledgment Number** → Direct SQL lookup
   - **Sport Schedule Query** → SQL query (`get_sport_schedule()`)
   - **Officer Lookup** → File search (`search_district_officer()`, etc.)
   - **Geo Query** → SQL query (`get_geo_details()`)
   - **Complex SQL** → SQL Agent (`run_sql_agent()`)
   - **General Question** → RAG Chain

3. **Response Generation**
   - Format: `{"text": str, "menus": list, "source": str, "session_id": str}`
   - Sources: `sql_database`, `rag_knowledge_base`, `menu_system`, `file_search`, etc.

---

## 🧠 Core Components

### **1. RAG Chain** (`rag/chain.py`)
- **Retriever**: Qdrant vector store with Gemini embeddings
- **LLM Manager**: `ask_llm()` handles:
  - Language detection
  - Model fallback (Gemini → OpenAI)
  - System prompt injection
  - Chat history management

### **2. Data Store** (`rag/data_store.py`)
- **Singleton Pattern**: In-memory SQLite database
- **Initialization**: Loads all CSVs from `data/csvs/` into tables
- **Views**: Creates secure views for LLM agent (`view_player_unified`, `view_sport_rules`)
- **Query Interface**: `ds.query(sql, params)` returns pandas DataFrame

### **3. LLM Manager** (`rag/llm_manager.py`)
- **Primary Model**: `gemini-2.5-flash`
- **Secondary Model**: `gpt-5.2-pro`
- **Features**:
  - Automatic language detection (`langdetect`)
  - Language-mirroring responses
  - Chat history support
  - Context injection

### **4. SQL Queries** (`rag/sql_queries.py`)
- **Predefined Functions**:
  - `get_player_venues_by_phone()` - Player venue lookup
  - `get_sport_schedule()` - Sport-specific schedules
  - `get_disciplines_by_level()` - Sports by tournament level
  - `get_geo_details()` - Location hierarchy lookup
  - `get_fixture_details()` - Match details
  - `get_sport_rules()` - Age criteria and eligibility

### **5. Location Search** (`rag/location_search.py`)
- **District Officers**: CSV lookup (`district_officers.csv`)
- **Cluster In-Charge**: Excel + Text file fallback
- **Mandal In-Charge**: Excel lookup (`MEO_Details.xlsx`)
- **Fuzzy Matching**: Uses `difflib` for approximate matching

### **6. Translations** (`rag/translations.py`)
- **Menu Translations**: Multilingual menu content (EN/TE/HI)
- **Structure**: `{("MENU_NAME", "lang_code"): {"text": str, "buttons": list}}`
- **Function**: `get_translation(menu_key, lang_code)`

---

## 🌐 API Endpoints

### **POST `/chat`**
- **Request**: `{"query": str, "session_id": Optional[str]}`
- **Response**: `{"text": str, "menus": list, "source": str, "session_id": str}`
- **Purpose**: Main chat endpoint with session management

### **POST `/ask`**
- **Request**: `{"query": str, "session_id": Optional[str]}`
- **Response**: Same as `/chat`
- **Purpose**: Alternative endpoint (legacy)

### **POST `/whatsappchat`**
- **Request**: `{"user_message": str, "phone_number": Optional[str]}`
- **Response**: Same as `/chat`
- **Purpose**: WhatsApp integration (uses phone as session_id)

### **GET `/health`**
- **Response**: `{"status": "ok"}`
- **Purpose**: Health check

### **GET `/`**
- **Response**: `{"status": "online", "message": "..."}`
- **Purpose**: Root endpoint

---

## 🔧 Data Pipeline

### **Ingestion Process** (`ingestion/run_ingestion.py`)

1. **Load Documents**
   - Source: `data/mdFiles/*.md`
   - Loader: `DirectoryLoader` with `TextLoader`

2. **Chunking** (`ingestion/chunking.py`)
   - Splits documents into smaller chunks
   - Configurable chunk size and overlap

3. **Embedding** (`ingestion/embed_store.py`)
   - **Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
   - **Note**: Retriever uses Gemini embeddings (768 dims) - potential mismatch!

4. **Storage**
   - **Vector DB**: Qdrant (local)
   - **Collection**: `rag_knowledge_base` (OpenAI) or `rag_knowledge_base_gemini` (Gemini)
   - **Batch Processing**: 50 chunks per batch

### **Data Sources**

#### **CSV Files** (`data/csvs/`)
- `player_details.csv` - Player registration data
- `tb_fixtures.csv` - Match schedules
- `tb_discipline.csv` - Sports/disciplines
- `tb_events.csv` - Event details
- `tb_category.csv` - Age categories
- `tb_selected_players.csv` - Selection status
- `districtmaster.csv`, `mandalmaster.csv`, `villagemaster.csv` - Geographic hierarchy
- `clustermaster.csv` - Cluster information
- `tb_district_officers.csv` - Officer details

#### **Excel Files** (`data/new data/`)
- `DistrictWIseClusters.xlsx` - Cluster in-charge details
- `MEO_Details.xlsx` - Mandal Educational Officer details

#### **Text Files** (`data/new data/`)
- `Mandal_Incharges_Cleaned.txt` - Fallback cluster in-charge data

---

## 🎨 Menu System

### **Menu Hierarchy**

```
MAIN_MENU
├── 1. Registration & Eligibility (MENU_REG_FAQ)
│   ├── 1.1 How to Register
│   ├── 1.2 Eligibility Rules
│   ├── 1.3 Documents Required
│   ├── 1.4 Registration Status
│   └── 1.5 FAQs
│
├── 2. Disciplines & Schedules (MENU_GROUP_SPORTS)
│   ├── 2.1 Disciplines (MENU_DISCIPLINES)
│   │   ├── Level 1: Cluster/Gram Panchayat
│   │   ├── Level 2: Mandal
│   │   ├── Level 3: Assembly
│   │   ├── Level 4: District
│   │   └── Level 5: State
│   │
│   ├── 2.2 Schedules (MENU_SCHEDULE)
│   │   ├── 2.2.1 Tournament Schedule (Static)
│   │   └── 2.2.2 Games Schedule (Dynamic)
│   │
│   └── 2.3 Medal Tally
│
├── 3. Venues & Officials (MENU_GROUP_VENUES)
│   ├── 3.1 Venues (Dynamic list)
│   ├── 3.2 District Officers
│   ├── 3.3 Venue In-Charge (Cluster)
│   └── 3.4 Mandal In-Charge (MEO)
│
├── 4. Player Status (MENU_PLAYER_STATUS)
│   ├── 4.1 Search by Phone No
│   └── 4.2 Search by Acknowledgment No
│
└── 5. Help & Language (MENU_GROUP_HELP)
    ├── 5.1 Helpline Numbers
    ├── 5.2 Email Support
    └── 5.3 Change Language
```

### **State Management**
- **SESSION_STATE**: Current menu/state (`MENU_MAIN`, `STATE_WAIT_PHONE`, etc.)
- **SESSION_DATA**: Session-specific data (`{"language": "en", "sports": [...], ...}`)
- **CHAT_SESSIONS**: Chat history per session (last 10 turns)

---

## 🔐 Security & Privacy

1. **PII Protection**
   - Aadhar numbers excluded from SQL views
   - Mobile numbers only used for lookup (not displayed in lists)
   - Secure SQL views for LLM agent

2. **SQL Injection Prevention**
   - Parameterized queries (`?` placeholders)
   - Restricted views for LLM agent
   - Query validation in SQL agent

3. **API Security**
   - CORS enabled (currently `allow_origins=["*"]`)
   - Input validation via Pydantic models

---

## 🚀 Deployment

### **Render.com** (Primary)
- **Config**: `render.yaml` (Blueprint)
- **Startup**: `start.sh` script
- **Process**:
  1. Install dependencies
  2. Convert CSVs to Markdown (if needed)
  3. Build vector database
  4. Start FastAPI server

### **Local Development**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export GOOGLE_API_KEY=...
export OPENAI_API_KEY=...

# 3. Run ingestion (if needed)
python ingest_full_gemini.py

# 4. Start server
uvicorn api.main:app --reload
```

---

## 🔍 Key Features

### **1. Multilingual Support**
- **Languages**: English, Hindi, Telugu
- **Detection**: Automatic via `langdetect`
- **Response**: Mirrors user's language
- **Menus**: Fully translated

### **2. Hybrid Intelligence**
- **Direct Lookup**: Phone/Ack number → Instant SQL results
- **SQL Queries**: Structured data queries
- **RAG**: General knowledge questions
- **Fallback**: LLM handles out-of-scope queries

### **3. Session Management**
- **Session ID**: UUID or phone number
- **State Persistence**: Menu navigation state
- **Chat History**: Last 10 conversation turns
- **Language Preference**: Stored per session

### **4. Smart Routing**
- **Regex Patterns**: Phone numbers, acknowledgment IDs, fixture IDs
- **Keyword Detection**: Sport names, officer types, locations
- **Intent Classification**: Menu navigation vs. query

---

## 📊 Data Flow Diagram

```
User Query
    │
    ├─→ Menu State Machine (Navigation)
    │       └─→ Menu Response
    │
    ├─→ Phone/Ack Number Detection
    │       └─→ SQL Direct Lookup
    │               └─→ Player Details
    │
    ├─→ Sport/Officer/Location Keywords
    │       └─→ SQL Query Functions
    │               └─→ Structured Data
    │
    ├─→ Complex SQL Intent
    │       └─→ SQL Agent (Text-to-SQL)
    │               └─→ LLM Generated SQL → Execute
    │
    └─→ General Query
            └─→ RAG Chain
                    ├─→ Vector Search (Qdrant)
                    ├─→ Retrieve Top-K Chunks
                    └─→ LLM Generation (Gemini/OpenAI)
                            └─→ Final Answer
```

---

## 🐛 Known Issues & Considerations

1. **Embedding Mismatch**
   - Ingestion uses OpenAI embeddings (1536 dims)
   - Retriever uses Gemini embeddings (768 dims)
   - **Impact**: Different collections needed

2. **In-Memory Database**
   - SQLite in-memory DB resets on restart
   - CSVs reloaded on each startup
   - **Consideration**: May be slow for large datasets

3. **Model Names**
   - Code references `gpt-5.2-pro` (may not exist)
   - Should verify model availability

4. **Error Handling**
   - Some functions return `None` on error
   - Inconsistent error messages
   - **Recommendation**: Standardize error responses

---

## 📝 Environment Variables

```env
GOOGLE_API_KEY=AI...          # Required (Gemini Embeddings & LLM)
OPENAI_API_KEY=sk-...         # Optional (Fallback LLM)
```

---

## 🧪 Testing

- **Test Files**: Located in `tests/` directory
- **Quick Test**: `python tests/run_quick_test.py`
- **Multilingual Test**: `python tests/test_multilingual.py`

---

## 📚 Key Dependencies

- **FastAPI**: Web framework
- **LangChain**: RAG orchestration
- **Qdrant**: Vector database
- **SQLite**: Structured data storage
- **Pandas**: Data manipulation
- **Google Generative AI**: Gemini embeddings & LLM
- **OpenAI**: Fallback LLM & embeddings
- **langdetect**: Language detection

---

## 🎯 Future Enhancements

1. **Unified Embeddings**: Use same embedding model for ingestion and retrieval
2. **Persistent Database**: Move from in-memory to file-based SQLite
3. **Caching**: Add Redis for frequently accessed data
4. **Analytics**: Track query patterns and user behavior
5. **Webhook Integration**: WhatsApp/Telegram webhooks
6. **Admin Dashboard**: Manage content and monitor system

---

## 📞 Support & Documentation

- **Setup Guides**: `SETUP_WINDOWS.md`, `SETUP_MAC.md`, `SETUP_LINUX.md`
- **Deployment**: `DEPLOYMENT_RENDER.md`
- **Main README**: `README.md`

---

**Last Updated**: Based on current codebase analysis
**Version**: 1.1.0 (as per `api/main.py`)
