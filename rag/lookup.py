import pandas as pd
from rag.sql_queries import search_players_sql

def format_player_card(p):
    """
    Formats a single player dictionary into Markdown.
    """
    # Helper to safely get values
    def get_val(key, default="N/A"):
        val = p.get(key)
        if val is None or str(val).lower() == "nan" or str(val).strip() == "":
            return default
        return str(val).strip()

    card = f"""
### 👤 Player Profile: {get_val('player_nm')}

**🆔 Registration ID:** `{get_val('player_reg_id')}`  
**📞 Mobile:** `{get_val('mobile_no')}`  
**🎂 Age/Gender:** {get_val('player_age')} / {get_val('gender')}  
**📍 Village:** {get_val('vill_gp_name')}

---
**🏛️ Cluster Details**  
**Name:** {get_val('clustername')}  
**Incharge:** {get_val('cluster_incharge')} ({get_val('incharge_mobile')})

---
**🏆 Game & Schedule**  
**Event:** {get_val('event_name')}  
**🏟️ Venue:** {get_val('venue', 'TBD')}  
**📅 Date:** {get_val('match_date', 'TBD')} ({get_val('match_day', 'TBD')}) @ {get_val('match_time', 'TBD')}

"""
    return card

def get_player_by_phone(phone_number):
    """
    Public API: Lookup by Phone (SQL Backend)
    """
    results = search_players_sql(phone_number, search_type="mobile")
    
    if not results:
        return f"❌ No Record Found for phone: {phone_number}"
    
    response = f"**Found {len(results)} Record(s)**\n"
    for p in results:
        response += format_player_card(p)
        
    return response

def get_player_by_reg_id(reg_id):
    """
    Public API: Lookup by Reg ID (SQL Backend)
    """
    results = search_players_sql(reg_id, search_type="reg_id")
    
    if not results:
        return f"❌ No Record Found for reg_id: {reg_id}"
    
    response = f"**Found {len(results)} Record(s)**\n"
    for p in results:
        response += format_player_card(p)
        
    return response
