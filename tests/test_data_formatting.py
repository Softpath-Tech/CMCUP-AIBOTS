from api.main import format_registrations
from rag.translations import MENU_TRANSLATIONS, get_msg

# Mock Session Data
mock_registrations = [{
    "player_nm": "Rishabh",
    "player_reg_id": "SATGCMC-123",
    "sport_name": "Cricket",
    "villagename": "VillageA",
    "mandalname": "MandalB",
    "districtname": "DistrictC",
    "is_state_level": 0,
    "is_district_level": 1,
    "venue": "Stadium X",
    "match_date": "2026-02-10",
    "cluster_incharge": "Officer Y",
    "incharge_mobile": "9999999999"
}]

# Helper to mock SESSION_DATA
from api.main import SESSION_DATA
session_en = "session_en"
session_te = "session_te"
session_hi = "session_hi"

SESSION_DATA[session_en] = {"language": "en"}
SESSION_DATA[session_te] = {"language": "te"}
SESSION_DATA[session_hi] = {"language": "hi"}

print("--- Testing English ---")
print(format_registrations(mock_registrations, session_en))
print("\n--- Testing Telugu ---")
print(format_registrations(mock_registrations, session_te))
print("\n--- Testing Hindi ---")
print(format_registrations(mock_registrations, session_hi))
