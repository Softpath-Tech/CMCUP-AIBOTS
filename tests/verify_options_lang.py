import sys
from unittest.mock import MagicMock

# Mock module before import
sys.modules['rag.sql_queries'] = MagicMock()
from rag.sql_queries import get_disciplines_by_level
get_disciplines_by_level.return_value = ["Sport A", "Sport B"]

# Import target
from api.main import get_discipline_response, SESSION_DATA

session_id = "test_sess_hi"
SESSION_DATA[session_id] = {"language": "hi"}

print("Testing Hindi Response for Level 3 (Assembly)...")
resp = get_discipline_response(3, session_id)
print(resp['text'])

if "विधानसभा क्षेत्र स्तर" in resp['text'] and "खेल चुनें" in resp['text']:
    print("✅ Hindi Verification Passed!")
else:
    print("❌ Hindi Verification Failed")
