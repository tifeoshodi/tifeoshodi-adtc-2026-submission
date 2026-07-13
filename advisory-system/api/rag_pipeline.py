import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
    print("Warning: llama_cpp_python not installed. Will run in mock mode.")

class LocalRAGPipeline:
    def __init__(self, model_path, embedding_model="all-MiniLM-L6-v2"):
        print("Initializing Local RAG Pipeline...")
        # Initialize the embedding model
        self.encoder = SentenceTransformer(embedding_model)
        
        # Initialize the FAISS index (using L2 distance)
        # all-MiniLM-L6-v2 produces 384-dimensional vectors
        self.index = faiss.IndexFlatL2(384)
        self.documents = []
        self.load_index()

        
        # Initialize the local LLM
        if os.path.exists(model_path):
            # Limit threads to avoid thermal throttling (e.g., 4 threads)
            self.llm = Llama(
                model_path=model_path,
                n_threads=4,
                n_ctx=2048, # Increased context window to accommodate chat history
                verbose=False
            )
        else:
            self.llm = None
            print(f"Warning: Model not found at {model_path}. Running in mock mode or wait for download.")

    def save_index(self, index_path="faiss_index.bin", docs_path="faiss_docs.json"):
        faiss.write_index(self.index, index_path)
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f)
        print(f"Index saved to {index_path} and documents to {docs_path}")

    def load_index(self, index_path="faiss_index.bin", docs_path="faiss_docs.json"):
        if os.path.exists(index_path) and os.path.exists(docs_path):
            self.index = faiss.read_index(index_path)
            with open(docs_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            print(f"Loaded index with {self.index.ntotal} vectors.")
            return True
        return False

    def ingest_document(self, text, chunk_size=100, overlap=20):
        """Splits text into overlapping chunks and adds to the FAISS index."""
        words = text.split()
        if not words:
            return
            
        paragraphs = []
        for i in range(0, len(words), max(1, chunk_size - overlap)):
            chunk = " ".join(words[i:i + chunk_size])
            paragraphs.append(chunk)
            if i + chunk_size >= len(words):
                break
        
        if not paragraphs:
            return
            
        embeddings = self.encoder.encode(paragraphs)
        # FAISS expects numpy float32 arrays
        embeddings = np.array(embeddings).astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        self.documents.extend(paragraphs)
        print(f"Ingested {len(paragraphs)} paragraphs.")

    def search(self, query, top_k=2):
        """Searches the vector store for the most relevant context."""
        if self.index.ntotal == 0:
            return []
            
        query_vector = self.encoder.encode([query])
        query_vector = np.array(query_vector).astype('float32')
        
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
        return results

    def ask(self, query, history=None):
        """Answers a query using RAG to prevent hallucination, with conversational memory."""
        if history is None:
            history = []
            
        context_chunks = self.search(query)
        context = "\n".join(context_chunks)
        
        prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are an agricultural assistant. ONLY use the provided context to answer. If you do not know, say 'I don't know'.\n\nContext:\n{context}<|eot_id|>\n"
        
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>\n"
            
        prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{query}<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n\n"

        if self.llm:
            response = self.llm(
                prompt,
                max_tokens=200,
                stop=["<|eot_id|>"],
                temperature=0.1
            )
            return response["choices"][0]["text"].strip()
        else:
            # Mock response if model is not loaded
            return f"[MOCK - Model missing]\nContext retrieved:\n{context}\n\nI would answer based on this."

# --- Usage Example ---
if __name__ == "__main__":
    model_file = "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    rag = LocalRAGPipeline(model_file)
    
    # Load sample data
    if os.path.exists("sample_data.txt"):
        with open("sample_data.txt", "r", encoding="utf-8") as f:
            data = f.read()
        rag.ingest_document(data)
    
    # Test query
    question = "How do I manage Cassava Mosaic Disease?"
    print(f"\nQuestion: {question}")
    answer = rag.ask(question)
    print(f"Answer: {answer}")
