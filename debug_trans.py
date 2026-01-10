from rag.translations import get_translation, MENU_TRANSLATIONS

print("--- Testing Translation Logic ---")
print(f"Total Translations: {len(MENU_TRANSLATIONS)}")

# Test Case 1: English
res_en = get_translation("TXT_REG_DOCS", "en")
print(f"EN: {res_en['text'][:20]}...")

# Test Case 2: Hindi
res_hi = get_translation("TXT_REG_DOCS", "hi")
print(f"HI: {res_hi['text'][:20]}...")

# Test Case 3: Telugu
res_te = get_translation("TXT_REG_DOCS", "te")
print(f"TE: {res_te['text'][:20]}...")

# Verify keys explicitly
print(f"Key ('TXT_REG_DOCS', 'hi') exists: {('TXT_REG_DOCS', 'hi') in MENU_TRANSLATIONS}")
