# Mac Setup Instructions

Follow these steps to set up and run the RAG Chatbot on a MacBook.

## 1. Prerequisites
- **Python 3.10+** (Install via Homebrew: `brew install python`)
- **Git**
- **OpenAI API Key** (Required for RAG)
- **Google API Key** (Optional, if using Gemini)

## 2. Clone and Install

Open your Terminal and run:

```bash
# Clone the repository (if you haven't already)
git clone <repository_url>
cd rag-chatbot

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Configuration (.env)

You need to set up your environment variables. 
Create a file named `.env` in the root folder (`rag-chatbot/.env`) and add your keys:

```bash
# Create the file
touch .env
open .env
```

**Paste the following inside .env:**

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

> **Note:** Get these keys from your friend if you don't have them, or use your own.

## 4. Initialize Data (Important!)

The vector database is not shared via Git, so you must build it locally using the provided data.

```bash
# 1. Convert CSV data to Markdown
python process_sql_data.py

# 2. Ingest data into Vector Database (Qdrant)
# Make sure you are in the root folder 'rag-chatbot'
python -m ingestion.run_ingestion
```

You should see a success message indicating `data/qdrant_db` has been created.

## 5. Run the Application

Start the API server:

```bash
uvicorn api.main:app --reload
```

The API will run at `http://127.0.0.1:8000`.

## 6. Verify

You can test if it's working by opening another terminal (remember to `source venv/bin/activate`) and running:

```bash
python tests/run_quick_test.py
```
