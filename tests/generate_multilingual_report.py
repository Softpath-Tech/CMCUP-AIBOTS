
import sys
import os
import json
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def run_session(lang_name, lang_option, queries):
    session_id = f"report_session_{lang_name}"
    print(f"\n--- {lang_name.upper()} SESSION ---")
    
    conversation = []

    # 1. Start
    resp = client.post("/chat", json={"query": "Hi", "session_id": session_id})
    conversation.append(("User", "Hi"))
    conversation.append(("Bot", resp.json()["response"]))

    # 2. Go to Help -> Language
    # Path: Main(5) -> Help(3) -> Select(Option)
    steps = ["5", "3", str(lang_option)]
    
    for step in steps:
        resp = client.post("/chat", json={"query": step, "session_id": session_id})
        conversation.append((f"User Input", step))
        conversation.append((f"Bot Response", resp.json()["response"]))

    # 3. Random Queries from argument
    for q in queries:
        resp = client.post("/chat", json={"query": q, "session_id": session_id})
        conversation.append((f"User Input", q))
        conversation.append((f"Bot Response", resp.json()["response"]))

    return conversation

def generate_report():
    report_data = {}
    
    # English Flow
    report_data["English"] = run_session("English", 1, ["1", "Back", "Jainad"])
    
    # Telugu Flow
    report_data["Telugu"] = run_session("Telugu", 2, ["4", "Back", "Bheempoor"])
    
    # Hindi Flow
    report_data["Hindi"] = run_session("Hindi", 3, ["3", "Back", "Bela"])

    # Output to Markdown
    with open("multilingual_test_report.md", "w", encoding="utf-8") as f:
        f.write("# Multilingual Chatbot Response Report\n\n")
        f.write("Generated from automated session simulation.\n\n")
        
        for lang, chat in report_data.items():
            f.write(f"## {lang} Session\n\n")
            for role, text in chat:
                f.write(f"**{role}:**\n{text}\n\n")
            f.write("---\n\n")
    
    print("\nReport generated: multilingual_test_report.md")

if __name__ == "__main__":
    generate_report()
