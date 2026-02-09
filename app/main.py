from fastapi import FastAPI
from pydantic import BaseModel
from app.rag.query_engine import answer_query

app = FastAPI(title="RAG Reliability API")

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query_rag(req: QueryRequest):
    return answer_query(req.query)
