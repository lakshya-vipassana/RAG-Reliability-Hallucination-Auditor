from app.rag.index import load_index
from app.config import TOP_K
MIN_SCORE=0.35
def retrieve(query: str):
    index = load_index()
    retriever = index.as_retriever(similarity_top_k=TOP_K)

    nodes = retriever.retrieve(query)

    results = []

    for node in nodes:
        if node.score < MIN_SCORE:
            continue
        results.append({
            "chunk_id": node.node_id,
            "text": node.text,
            "score": node.score,
            "metadata": node.metadata
        })

    return results
