import pandas as pd
from rag.sql_queries import search_players_sql

def format_player_card(p):
    """
    Formats a single player dictionary into a compact Markdown card.
    """
    def get_val(key, default="N/A"):
        val = p.get(key)
        if val is None or str(val).lower() == "nan" or str(val).strip() in ["", "0"]:
            return default
        return str(val).strip()

    # Map Values
    gender_map = {'1': 'Male', '2': 'Female', 'M': 'Male', 'F': 'Female', '0': 'Female'}
    gender_raw = str(p.get('gender', '')).strip()
    gender_disp = gender_map.get(gender_raw, gender_raw if gender_raw else 'N/A')

    # Level Logic
    level_list = []
    if str(p.get('is_state_level')) == '1': level_list.append("State")
    if str(p.get('is_district_level')) == '1': level_list.append("District")
    if str(p.get('is_mandal_level')) == '1': level_list.append("Mandal")
    
    current_level = f"🏅 **Selected for {level_list[0]} Level**" if level_list else "Starting Level"

    # Helpers for conditional display
    def should_show(val):
        return val and val not in ["N/A", "TBD", ""]

    # Construct clean card
    # Header Section
    card = f"""
> **👤 PLAYER PROFILE: {get_val('player_nm')}**
>
> | **Info** | **Details** |
> | :--- | :--- |
> | 🆔 **Reg ID** | `{get_val('player_reg_id')}` |
> | 🚻 **Gender** | {gender_disp} |
> | 🎂 **Age** | {get_val('player_age')} Years |
> | 📍 **Location** | {get_val('vill_gp_name')} |
> | 📊 **Status** | {current_level} |
>
> ---
"""
    
    # Game Section (Conditional)
    game_lines = []
    sport = get_val('sport_name', get_val('event_name'))
    event = get_val('event_name')
    venue = get_val('venue', 'TBD')
    m_date = get_val('match_date', 'TBD')
    m_day = get_val('match_day', '')
    m_time = get_val('match_time', '')

    if should_show(sport): game_lines.append(f"> * **Sport:** {sport}")
    if should_show(event) and event != sport: game_lines.append(f"> * **Event:** {event}")
    if should_show(venue) and venue != "TBD": game_lines.append(f"> * **🏟️ Venue:** {venue}")
    
    # Schedule logic: Only show if Date or Time is real
    schedule_str = ""
    if should_show(m_date) and m_date != "TBD": schedule_str += f"{m_date} "
    if should_show(m_day): schedule_str += f"| {m_day} "
    if should_show(m_time): schedule_str += f"@ {m_time}"
    
    if schedule_str: game_lines.append(f"> * **📅 Time:** {schedule_str}")

    if game_lines:
        card += "> **🏆 GAME & SCHEDULE**\n" + "\n".join(game_lines) + "\n>\n> ---\n"


    # Cluster Section (Conditional)
    cluster_lines = []
    c_name = get_val('clustername')
    c_incharge = get_val('cluster_incharge')
    c_mobile = get_val('incharge_mobile')

    if should_show(c_name) and c_name != "N/A": cluster_lines.append(f"> * **Cluster:** {c_name}")
    if should_show(c_incharge) and c_incharge != "N/A": cluster_lines.append(f"> * **Incharge:** {c_incharge}")
    if should_show(c_mobile) and c_mobile != "N/A": cluster_lines.append(f"> * **📞 Mobile:** `{c_mobile}`")

    if cluster_lines:
        card += "> **🏛️ CLUSTER CONTACT**\n" + "\n".join(cluster_lines) + "\n"
    
    # Close Quote if last section empty
    if not cluster_lines and not game_lines:
        card += "\n"

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
