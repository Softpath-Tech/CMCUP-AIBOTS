
import requests
import json
import time

API_URL = "http://localhost:8000/chat"

def main():
    print("🤖 RAG Chatbot CLI Tester")
    print(f"📡 Connecting to: {API_URL}")
    print("EXIT/QUIT to stop.\n")
    
    # Check health
    try:
        requests.get("http://localhost:8000/health", timeout=2)
        print("✅ API is Online!\n")
    except:
        print("❌ API seems offline. Make sure 'uvicorn api.main:app' is running.")
        return

    while True:
        try:
            query = input("You: ").strip()
            if not query: continue
            if query.lower() in ["exit", "quit", "q"]:
                break
                
            start = time.time()
            try:
                response = requests.post(
                    API_URL, 
                    json={"query": query},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                latency = round(time.time() - start, 2)
                
                if response.status_code == 200:
                    data = response.json()
                    ans = data.get("response", "No response text")
                    src = data.get("source", "Unknown")
                    
                    print(f"\n🤖 Bot ({latency}s) [{src}]:\n{'-'*40}")
                    print(ans)
                    print(f"{'-'*40}\n")
                else:
                    print(f"\n❌ Error {response.status_code}:\n{response.text}\n")
                    
            except requests.exceptions.Timeout:
                print("\n❌ Request Timed Out (30s)\n")
            except requests.exceptions.ConnectionError:
                print("\n❌ Connection Failed. Is the server running?\n")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
