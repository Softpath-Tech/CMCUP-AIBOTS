import sqlite3
import pandas as pd
import os

DB_PATH = "rag/cm_cup.db" # Initial guess, will update after checking data_store.py

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    # Try finding it
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".db"):
                print(f"Found DB: {os.path.join(root, file)}")
                DB_PATH = os.path.join(root, file)
                break
        if os.path.exists(DB_PATH): break

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Check for likely candidates
    for t in tables:
        name = t[0]
        if "officer" in name.lower() or "incharge" in name.lower() or "district" in name.lower():
            print(f"Schema for {name}:")
            cursor.execute(f"PRAGMA table_info({name})")
            print(cursor.fetchall())
            print(f"Sample data for {name}:")
            cursor.execute(f"SELECT * FROM {name} LIMIT 3")
            print(cursor.fetchall())
    conn.close()
