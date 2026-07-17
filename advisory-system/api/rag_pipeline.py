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

    def ingest_document(self, text, max_words=200):
        """Splits text into semantic paragraphs and adds to the FAISS index with source metadata."""
        import re
        words = text.split()
        if not words:
            return
            
        paragraphs = []
        
        # Split the text by double newlines to preserve paragraph boundaries
        raw_chunks = re.split(r'\n\s*\n', text)
        
        current_source = "Unknown Source"
        current_chunk = []
        current_word_count = 0
        
        for p in raw_chunks:
            p = p.strip()
            if not p:
                continue
                
            # Detect source headers
            source_match = re.match(r'^--- SOURCE:\s*(.*?)\s*---$', p)
            if source_match:
                # If we have a pending chunk, save it
                if current_chunk:
                    paragraphs.append(f"Source: {current_source}\n" + " ".join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                current_source = source_match.group(1)
                continue
                
            words_in_p = p.split()
            word_count = len(words_in_p)
            
            if current_word_count + word_count > max_words and current_chunk:
                paragraphs.append(f"Source: {current_source}\n" + " ".join(current_chunk))
                current_chunk = []
                current_word_count = 0
                
            current_chunk.append(p)
            current_word_count += word_count
            
        if current_chunk:
            paragraphs.append(f"Source: {current_source}\n" + " ".join(current_chunk))
        
        if not paragraphs:
            return
            
        embeddings = self.encoder.encode(paragraphs)
        # FAISS expects numpy float32 arrays
        embeddings = np.array(embeddings).astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        self.documents.extend(paragraphs)
        print(f"Ingested {len(paragraphs)} semantic paragraphs with metadata.")

    def search(self, query, top_k=5):
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
        
        prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are an expert Agricultural Extension Assistant. You must strictly follow these rules:\n1. PRIMARY SOURCE: For questions about specific farming practices (e.g., planting dates, disease management, methods), you MUST use ONLY the facts found in the provided Context.\n2. MISSING INFO: If the Context lacks the specific facts needed for a practice-related question, you MUST output exactly: 'I don't know'. DO NOT guess or hallucinate.\n3. GENERAL KNOWLEDGE: For general definitions or basic crop concepts (e.g., 'What is a yam?'), you may use your internal knowledge to provide a brief, factual answer.\n4. SAFETY: NEVER recommend specific chemical dosages or unverified treatments unless explicitly stated in the Context.\n5. TONE: Answer directly and professionally. NEVER mention the context (e.g., do not say 'According to the text').<|eot_id|>\n"
        
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>\n"
            
        prompt += f"<|start_header_id|>user<|end_header_id|>\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer the question naturally and directly as an expert. Remember: ONLY use facts from the context. If the answer is not in the context, just say 'I don't know'.<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n\n"

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
    model_file = "../../model/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
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
