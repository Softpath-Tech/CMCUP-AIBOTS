import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure project root is in path
sys.path.append(os.getcwd())

# Import api.main to be tested
# mocking rag components to avoid database hits
with patch.dict(sys.modules, {'rag.chain': MagicMock(), 'rag.sql_queries': MagicMock()}):
    import api.main as main_api

class TestLanguageConsistency(unittest.TestCase):
    
    def setUp(self):
        # Reset Session Data
        main_api.SESSION_DATA = {}
        main_api.SESSION_STATE = {}

    def test_get_msg_en(self):
        main_api.SESSION_DATA = {"sess1": {"language": "en"}}
        msg = main_api.get_msg("ERR_INVALID_PHONE", "sess1")
        print(f"EN Msg: {msg}")
        self.assertIn("Invalid Phone Number", msg)

    def test_get_msg_te(self):
        main_api.SESSION_DATA = {"sess1": {"language": "te"}}
        msg = main_api.get_msg("ERR_INVALID_PHONE", "sess1")
        print(f"TE Msg: {msg}")
        self.assertIn("చెల్లని ఫోన్ నంబర్", msg)

    def test_get_msg_hi(self):
        main_api.SESSION_DATA = {"sess1": {"language": "hi"}}
        msg = main_api.get_msg("ERR_INVALID_PHONE", "sess1")
        print(f"HI Msg: {msg}")
        self.assertIn("अमान्य फोन नंबर", msg)
    
    def test_dynamic_formatting(self):
        main_api.SESSION_DATA = {"sess1": {"language": "te"}}
        # ERR_NO_REGISTRATION has {phone} placeholder
        msg = main_api.get_msg("ERR_NO_REGISTRATION", "sess1", phone="1234567890")
        print(f"Dynamic TE Msg: {msg}")
        self.assertIn("1234567890", msg)
        self.assertIn("కనుగొనబడలేదు", msg)

if __name__ == '__main__':
    unittest.main()
