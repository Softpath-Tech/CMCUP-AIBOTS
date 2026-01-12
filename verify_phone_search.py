import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from rag.data_store import get_datastore
from rag.sql_queries import get_player_venues_by_phone

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("verify_log.txt", "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger()

def verify_phone_search():
    print("Initializing DataStore...")
    ds = get_datastore()
    if not ds.initialized:
        ds.init_db()

    # 1. Find a mobile number with multiple registrations
    print("\nSearching for a mobile number with multiple registrations...")
    query_multi = """
    SELECT mobile_no, COUNT(*) as cnt 
    FROM player_details 
    GROUP BY mobile_no 
    HAVING cnt > 1 
    LIMIT 1
    """
    df_multi = ds.query(query_multi)
    
    if df_multi.empty:
        print("No multi-registration numbers found. Trying single registration...")
        query_single = "SELECT mobile_no FROM player_details LIMIT 1"
        df_single = ds.query(query_single)
        if df_single.empty:
            print("No players found in database!")
            return
        phone = df_single.iloc[0]['mobile_no']
    else:
        phone = df_multi.iloc[0]['mobile_no']
        count = df_multi.iloc[0]['cnt']
        print(f"Found number {phone} with {count} registrations.")

    # 2. Test get_player_venues_by_phone
    print(f"\nTesting get_player_venues_by_phone('{phone}')...")
    results = get_player_venues_by_phone(phone)
    
    print(f"\nResults found: {len(results)}")
    for i, res in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        for k, v in res.items():
            print(f"{k}: {v}")

    # 3. Simulate API response logic
    print("\n--- Simulated API Response Logic ---")
    if len(results) == 1:
        rec = results[0]
        venue = rec.get('venue')
        sport = rec.get('sport_name') or rec.get('event_name')
        
        txt = f"### 🏟️ Venue Details for {sport}\n"
        if venue:
            txt += f"**Venue:** {venue}\n"
            txt += f"**Date:** {rec.get('match_date') or 'Check Schedule'}\n"
        else:
            txt += "**Status:** Venue details pending/TBD.\n"
        
        if rec.get('cluster_incharge'):
             txt += f"\n👤 **Venue In-Charge:** {rec.get('cluster_incharge')}\n"
             txt += f"📞 **Contact:** {rec.get('incharge_mobile', 'N/A')}\n"
        print(txt)
        
    else:
        # Multiple Records - Deduplicate by player_reg_id
        unique_map = {}
        for r in results:
            rid = r.get('player_reg_id')
            key = rid if rid else f"unknown_{len(unique_map)}"
            if key not in unique_map:
                unique_map[key] = r
        
        unique_recs = list(unique_map.values())
        
        txt = f"found **{len(unique_recs)} registrations** for this number:\n"
        for r in unique_recs:
            s = r.get('sport_name') or r.get('event_name')
            e = r.get('event_name')
            ack = r.get('player_reg_id')
            
            # Format: - Sport (Event) [Ack: ...]
            entry = f"- **{s}**"
            if e and s != e: entry += f" ({e})"
            if ack: entry += f" [`{ack}`]"
            
            txt += f"{entry}\n"
        
        txt += "\nSince you have multiple events, please COPY the **Acknowledgment Number** (e.g., SATGCMC-...) above and paste it here to get venue details."
        print(txt)

if __name__ == "__main__":
    verify_phone_search()
