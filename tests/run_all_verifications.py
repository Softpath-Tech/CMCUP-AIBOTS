
import subprocess
import sys
import os

def run_script(script_path):
    print(f"\n🚀 RUNNING: {script_path}...")
    try:
        # Force UTF-8 encoding to handle emojis in output on Windows
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            encoding='utf-8', 
            errors='replace'
        )
    except Exception as e:
        print(f"❌ EXECUTION FAILED: {e}")
        return False
    if result.returncode == 0:
        print(f"✅ PASS")
        # Optional: Print subset of output if needed
        # print(result.stdout[:200] + "...") 
    else:
        print(f"❌ FAIL")
        print("--- STDERR ---")
        print(result.stderr)
        print("--- STDOUT ---")
        print(result.stdout)
        return False
    return True

def main():
    print("=== 🛡️ SYSTEM VERIFICATION SUITE 🛡️ ===\n")
    
    scripts = [
        "tests/verify_phone_scenarios.py",
        "tests/verify_menu_player_status.py",
        "reproduce_500_error.py",
        "tests/verify_data_mapping.py"
    ]
    
    passed = 0
    failed = 0
    
    for s in scripts:
        if run_script(s):
            passed += 1
        else:
            failed += 1
            
    print(f"\n\n📊 RESULTS: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("✅ ALL SYSTEMS GO. READY FOR PUSH.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED. DO NOT PUSH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
