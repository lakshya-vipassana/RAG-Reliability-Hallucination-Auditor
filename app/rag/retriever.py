# app/rag/retriever.py
from app.rag.index import load_index
from app.config import TOP_K

MIN_SCORE = 0.0

def retrieve_chunks(query: str):
    """
    Retrieve top-k chunks above a minimum similarity score.
    """
    index = load_index()
    retriever = index.as_retriever(similarity_top_k=TOP_K)
    nodes = retriever.retrieve(query)
    print("RAW NODES:", nodes)


    results = []
    for node in nodes:
        if node.score is not None and node.score < MIN_SCORE:
            continue
        source = None
        metadata = node.metadata or {}
        if isinstance(metadata, dict):
            source = metadata.get("file_name") or metadata.get("file_path")
        results.append({
            "chunk_id": node.node_id,
            "text": node.text,
            "score": node.score,
            "metadata": node.metadata,
            "source": source
        })
        print("FILTERED RESULTS:", results)

    return results
