import pandas as pd
import os

# --- CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
CSV_DIR = os.path.join(project_root, "data", "csvs")

def clean_text(text):
    """Fixes 'nan' and empty values."""
    s = str(text).strip()
    if s.lower() in ['nan', 'null', 'none', '', 'nat']:
        return "N/A"
    return s

def get_level_from_code(code):
    """
    Maps the numeric 'is_level_code' to the actual Hierarchy Text.
    1 -> Village, 2 -> Mandal, 3 -> Assembly, 4 -> District, 5 -> State
    """
    s = str(code).strip()
    
    # MAPPING LOGIC
    if s == '1': return "📍 **Village / Cluster Level**"
    if s == '2': return "🥈 **MANDAL Level**"
    if s == '3': return "🏛️ **ASSEMBLY Constituency Level**"
    if s == '4': return "🥇 **DISTRICT Level**"
    if s == '5': return "🏆 **STATE Level**"
    
    return None

def get_player_status(phone_number):
    # 1. Load Data
    try:
        df_players = pd.read_csv(os.path.join(CSV_DIR, "player_details.csv"), dtype=str)
        df_selected = pd.read_csv(os.path.join(CSV_DIR, "tb_selected_players.csv"), dtype=str)
        df_results = pd.read_csv(os.path.join(CSV_DIR, "tb_player_results.csv"), dtype=str)
        
        # Clean Headers
        for df in [df_players, df_selected, df_results]:
            df.columns = df.columns.str.strip().str.lower()
            
        # Fix ID Mapping
        if 'player_id' not in df_players.columns and 'id' in df_players.columns:
            df_players['player_id'] = df_players['id']

    except Exception as e:
        return f"⚠️ System Error: {str(e)}"

    # 2. Find Player
    clean_phone = str(phone_number).replace("+91", "").replace("-", "").replace(" ", "").strip()
    player_row = df_players[df_players['mobile_no'] == clean_phone]

    if player_row.empty:
        return f"❌ No Record Found for {clean_phone}"

    # 3. Extract Details
    row = player_row.iloc[0]
    pid = clean_text(row.get('player_id'))
    name = clean_text(row.get('player_nm'))
    reg_id = clean_text(row.get('player_reg_id'))
    village = clean_text(row.get('vill_gp_name'))
    age = clean_text(row.get('player_age'))
    
    # Gender
    gender_val = str(row.get('gender', '')).strip()
    gender = "Male" if gender_val in ['1', '1.0'] else "Female" if gender_val in ['2', '2.0'] else "Other"

    # 4. Determine Level & Status (Using Level Code)
    status_msg = "✅ **Active**" # Default if they exist
    level_msg = "📍 Village / Cluster Level" # Default base
    
    # Check 'is_level_code' in player_details (Primary Source)
    level_code = row.get('is_level_code')
    decoded_level = get_level_from_code(level_code)
    
    if decoded_level:
        level_msg = decoded_level
    
    # Also Check Selection Table for Override/Confirmation
    if 'player_id' in df_selected.columns:
        sel_row = df_selected[df_selected['player_id'] == pid]
        if not sel_row.empty:
            s_row = sel_row.iloc[0]
            # Check if selection table has a higher/newer level code
            sel_code = s_row.get('is_level_code')
            sel_decoded = get_level_from_code(sel_code)
            if sel_decoded:
                level_msg = sel_decoded
                
            # Check selection status
            is_sel = str(s_row.get('is_select', '')).strip().lower()
            if is_sel in ['1', '1.0', 'true', 'yes']:
                status_msg = "✅ **SELECTED**"
            elif is_sel in ['0', '0.0', 'false', 'no']:
                status_msg = "❌ Not Selected in recent round"

    # 5. Check Score
    score_msg = "No score yet"
    if 'player_id' in df_results.columns:
        res_row = df_results[df_results['player_id'] == pid]
        if not res_row.empty:
            score_msg = clean_text(res_row.iloc[0].get('score'))

    # 6. Final Card
    return (
        f"**📋 CM CUP PLAYER STATUS**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** {name}\n"
        f"🆔 **Reg ID:** {reg_id}\n"
        f"📍 **Village/GP:** {village}\n"
        f"🎂 **Age/Gender:** {age} Yrs / {gender}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 **Current Status:**\n"
        f"• **Status:** {status_msg}\n"
        f"• **Current Level:** {level_msg}\n"
        f"• **Score:** {score_msg}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

if __name__ == "__main__":
    print(get_player_status('8328508582'))