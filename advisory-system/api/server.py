from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_pipeline import LocalRAGPipeline
import os
import asyncio
from contextlib import asynccontextmanager

rag = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    model_path = "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    rag = LocalRAGPipeline(model_path)
    
    if rag.index.ntotal == 0:
        if os.path.exists("sample_data.txt"):
            with open("sample_data.txt", "r", encoding="utf-8") as f:
                data = f.read()
            rag.ingest_document(data)
            rag.save_index()
    yield

app = FastAPI(title="Agricultural Advisory API", lifespan=lifespan)


# Allow Tauri frontend to communicate with local API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost", "http://localhost:5173", "http://127.0.0.1:1420", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

class ChatResponse(BaseModel):
    reply: str
    context_used: list[str]

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    # Get the context used for transparency in the UI
    context_chunks = rag.search(request.message)
    
    # Get the LLM answer, passing the history
    answer = await asyncio.to_thread(rag.ask, request.message, request.history)

    
    return ChatResponse(
        reply=answer,
        context_used=context_chunks
    )

@app.get("/api/health")
async def health_check():
    if not rag:
        return {"status": "starting", "model_loaded": False}
    return {"status": "ok", "model_loaded": rag.llm is not None}

@app.post("/api/rebuild_index")
async def rebuild_index():
    global rag
    if not rag:
        raise HTTPException(status_code=500, detail="RAG Pipeline not initialized")
        
    rag.documents = []
    rag.index.reset()
    
    if os.path.exists("real_agri_data.txt"):
        with open("real_agri_data.txt", "r", encoding="utf-8") as f:
            data = f.read()
        rag.ingest_document(data)
    elif os.path.exists("sample_data.txt"):
        with open("sample_data.txt", "r", encoding="utf-8") as f:
            data = f.read()
        rag.ingest_document(data)
        
    rag.save_index()
    return {"status": "ok", "indexed_vectors": rag.index.ntotal}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
