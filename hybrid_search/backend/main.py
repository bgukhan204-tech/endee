from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .hybrid_search import HybridSearchEngine
from .sample_data import sample_documents

app = FastAPI(title="Hybrid Search API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine
engine = HybridSearchEngine(sample_documents)

class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5

@app.get("/")
async def root():
    return {"message": "Hybrid Search API is running"}

@app.get("/documents")
async def get_documents():
    return sample_documents

@app.post("/search")
async def search(search_query: SearchQuery):
    if not search_query.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        results = engine.search(search_query.query, top_k=search_query.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
