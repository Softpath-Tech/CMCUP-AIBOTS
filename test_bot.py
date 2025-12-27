import sys
import os

# Ensure we can find the 'rag' folder
sys.path.append(os.getcwd())

from rag.chain import get_rag_chain

def main():
    print("🤖 Loading the Bot...")
    
    try:
        # 1. Load the Brain
        chain = get_rag_chain()
        
        # 2. Ask a Question
        question = "What is the website about?"
        print(f"\n🗣️  User Question: {question}")
        print("thinking...")
        
        # 3. Get Answer (Simple String Return)
        response = chain.invoke(question)
        
        print(f"\n🤖 Bot Answer: {response}")
        print("\n✅ RAG System is WORKING!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    main()