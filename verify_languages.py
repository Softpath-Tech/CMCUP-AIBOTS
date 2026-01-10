from rag.translations import MENU_TRANSLATIONS

def audit_translations():
    # 1. Identify all unique keys (base keys like MENU_MAIN, TXT_REG_DOCS)
    base_keys = set()
    for key, lang in MENU_TRANSLATIONS.keys():
        base_keys.add(key)
    
    print(f"Found {len(base_keys)} unique translation keys.")
    
    languages = ['en', 'hi', 'te']
    missing = {code: [] for code in languages}
    
    for key in sorted(base_keys):
        for lang in languages:
            if (key, lang) not in MENU_TRANSLATIONS:
                missing[lang].append(key)
    
    print("\n--- MISSING TRANSLATIONS ---")
    has_errors = False
    for lang, keys in missing.items():
        if keys:
            has_errors = True
            print(f"\nExample missing in '{lang}':")
            for k in keys:
                print(f"  - {k}")
        else:
            print(f"\n✅ All keys present for '{lang}'")

    if not has_errors:
        print("\n✅ GREAT! All menu keys have translations in all 3 languages.")

if __name__ == "__main__":
    audit_translations()
