
from fastapi.testclient import TestClient
import sys
import os
import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def test_main_menu_keywords():
    """Verify variations of 'Main Menu' work"""
    session_id = "test_nav_main"
    
    # Init
    client.post("/chat", json={"query": "hi", "session_id": session_id})
    
    # Navigate away
    client.post("/chat", json={"query": "1", "session_id": session_id}) # To Registration
    
    # Try keywords
    for keyword in ["main menu", "menu main", "home", "start"]:
        print(f"Testing keyword: {keyword}")
        resp = client.post("/chat", json={"query": keyword, "session_id": session_id})
        data = resp.json()
        ans = data.get("text") or data.get("response") or ""
        assert "Welcome to Telangana Sports Authority" in ans, f"Failed for keyword: {keyword}"

def test_menu_shortcuts():
    """Verify keyword shortcuts jump to menus"""
    session_id = "test_nav_shortcuts"
    
    shortcuts = {
        "registration": "Registration & Eligibility",
        "i want to register": "Registration & Eligibility",
        "show me sports": "Sports & Matches",
        "game schedule": "Sports & Matches",
        "venues": "Venues & Officials",
        "who is the officer": "Venues & Officials",
        "check player status": "Player Status",
        "help": "Help & Language"
    }
    
    for query, expected_text in shortcuts.items():
        print(f"Testing shortcut: '{query}' -> Expecting '{expected_text}'")
        resp = client.post("/chat", json={"query": query, "session_id": session_id})
        data = resp.json()
        ans = data.get("text") or data.get("response") or ""
        assert expected_text in ans or expected_text.split("&")[0].strip() in ans, f"Failed for query: {query}"

if __name__ == "__main__":
    test_main_menu_keywords()
    test_menu_shortcuts()
    print("✅ All Navigation Intent Tests Passed")
