from rag_pipeline import LocalRAGPipeline

def run_tests():
    print("Loading RAG Pipeline...")
    rag = LocalRAGPipeline('models/Llama-3.2-1B-Instruct-Q4_K_M.gguf')
    
    queries = [
        "How do I manage Fall Armyworm on my maize?",
        "What are the best practices for Yam storage to prevent rotting?",
        "Can you explain how to set up a Banana tissue culture nursery?"
    ]
    
    print("\n--- RUNNING TEST QUERIES ---\n")
    for q in queries:
        print(f"QUERY: {q}")
        print("-" * 40)
        answer = rag.ask(q)
        print(f"RESPONSE:\n{answer}")
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    run_tests()
