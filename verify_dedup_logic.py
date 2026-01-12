
def verify_logic():
    # Sample data mimicking the DB output
    registrations = [
        {"sport_name": "Athletics", "event_name": "200M", "player_reg_id": "SATGCMC-004"},
        {"sport_name": "Athletics", "event_name": "400M", "player_reg_id": "SATGCMC-005"},
        {"sport_name": "Kho-Kho", "event_name": None, "player_reg_id": "SATGCMC-006"},
        {"sport_name": "Kho-Kho", "event_name": None, "player_reg_id": "SATGCMC-006"}, # Dup
        {"sport_name": "Kho-Kho", "event_name": None, "player_reg_id": "SATGCMC-006"}, # Dup
        {"sport_name": "Badminton", "event_name": "Singles", "player_reg_id": "SATGCMC-007"},
    ]
    
    print(f"Original Count: {len(registrations)}")
    
    # New Logic
    unique_map = {}
    for r in registrations:
        rid = r.get('player_reg_id')
        if rid:
            # Use the first occurrence
            if rid not in unique_map:
                unique_map[rid] = r
            else:
                # Optional: Merge details if needed, but for listing, first is fine
                pass
    
    unique_recs = list(unique_map.values())
    print(f"Unique Count: {len(unique_recs)} (Expected 4)")
    
    txt = f"found **{len(unique_recs)} registrations** for this number:\n"
    for r in unique_recs:
        s = r.get('sport_name')
        e = r.get('event_name')
        ack = r.get('player_reg_id')
        
        # Format: - Sport (Event) [Ack: ...]
        entry = f"- **{s}**"
        if e: entry += f" ({e})"
        if ack: entry += f" [`{ack}`]"
        
        txt += f"{entry}\n"
    
    txt += "\nSince you have multiple events, please COPY the **Acknowledgment Number** (e.g., SATGCMC-...) above and paste it here to get venue details."
    
    print("\n--- Generated Response ---")
    print(txt)

if __name__ == "__main__":
    verify_logic()
