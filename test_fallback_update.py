from rag.llm_manager import ask_llm

def test_fallback():
    print("--- Testing Out-of-Scope Fallback ---")
    # A query that is definitely out of scope for SATG Sports
    query = "What is the recipe for chocolate cake?"
    context = "Informational context about sports only."
    
    result = ask_llm(context, query)
    print(f"Query: {query}")
    print(f"Response: {result['response']}")
    
    expected_content = "SATG Sports Assistant"
    if expected_content in result['response']:
        print("✅ Success: New fallback message detected!")
    else:
        print("❌ Failure: New fallback message NOT detected.")

    print("\n--- Testing Absence Fallback ---")
    # A sports query that won't be in the context
    query = "Who won the CM Cup in 1950?"
    context = "Context only mentions 2025 and 2026 events."
    
    result = ask_llm(context, query)
    print(f"Query: {query}")
    print(f"Response: {result['response']}")
    
    if expected_content in result['response']:
        print("✅ Success: New fallback message detected!")
    else:
        print("❌ Failure: New fallback message NOT detected.")

if __name__ == "__main__":
    test_fallback()
