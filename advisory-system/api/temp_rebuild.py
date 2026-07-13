import os
from rag_pipeline import LocalRAGPipeline

def rebuild():
    print("Initializing pipeline...")
    rag = LocalRAGPipeline('models/Llama-3.2-1B-Instruct-Q4_K_M.gguf')
    
    print("Resetting old index...")
    rag.index.reset()
    rag.documents = []
    
    print("Reading new real_agri_data.txt...")
    with open('real_agri_data.txt', 'r', encoding='utf-8') as f:
        data = f.read()
        
    print(f"Read {len(data)} characters. Ingesting...")
    rag.ingest_document(data)
    
    print(f"Saving new index with {rag.index.ntotal} vectors...")
    rag.save_index()
    print("Done!")

if __name__ == "__main__":
    rebuild()
