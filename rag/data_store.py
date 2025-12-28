import sqlite3
import pandas as pd
import os
import glob

class DataStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataStore, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect(":memory:", check_same_thread=False)
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance.initialized = False
        return cls._instance

    def init_db(self, csv_dir="data/csvs"):
        if self.initialized:
            print("✅ DataStore already initialized.")
            return

        print("⚡ Initializing SQLite Data Store...")
        
        # Load all CSVs
        csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
        for f in csv_files:
            try:
                table_name = os.path.splitext(os.path.basename(f))[0]
                # Read CSV
                df = pd.read_csv(f, dtype=str)
                # Clean headers: lowercase, strip
                df.columns = df.columns.str.strip().str.lower()
                
                # Write to SQLite
                df.to_sql(table_name, self.conn, if_exists="replace", index=False)
                print(f"   -> Loaded table: {table_name} ({len(df)} rows)")
            except Exception as e:
                print(f"   ❌ Error loading {f}: {e}")

        # Create Indices for Performance
        indices = [
            ("player_details", "mobile_no"),
            ("player_details", "player_reg_id"),
            ("player_details", "id"),
            ("villagemaster", "villagename"),
            ("villagemaster", "cluster_id"),
            ("clustermaster", "cluster_id"),
            ("tb_events", "id"),
            ("tb_fixtures", "disc_id")
        ]
        
        for table, col in indices:
            try:
                self.conn.execute(f"CREATE INDEX idx_{table}_{col} ON {table}({col})")
            except Exception:
                pass # Table or col might not exist

        self.initialized = True
        print("✅ DataStore Ready!")

    def query(self, query, params=()):
        return pd.read_sql_query(query, self.conn, params=params)

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

# Global Accessor
def get_datastore():
    return DataStore()
