from fastapi import FastAPI
from pydantic import BaseModel

from app.rag.answering import answer_query

app = FastAPI(title="RAG Reliability & Hallucination Auditor")

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query_rag(req: QueryRequest):
    return answer_query(req.query)
