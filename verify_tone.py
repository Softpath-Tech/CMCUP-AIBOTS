import requests
import json

def test_query(query, description):
    print(f"\n🔎 Testing [{description}]: '{query}'")
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            res_json = response.json()
            print("Response:\n" + ("-"*40))
            print(res_json.get("response"))
            print("-" * 40)
        else:
            print(f"❌ Error {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    # 1. Structure Check: Should list sports in bullets
    test_query("games", "Structure: Sports List")
    
    # 2. Tone Check: Should be formal
    test_query("eligibility", "Tone: Eligibility")

    # 3. Hard Rule Check: Should not align with out of context
    test_query("How to bake a cake?", "Hard Rule: Irrelevant")
