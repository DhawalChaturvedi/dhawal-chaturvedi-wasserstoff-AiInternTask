from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from app.services.vector_db import search, search_in_document, get_all_chunks
from app.services.theme_synthesis import identify_themes
from app.services.theme import cluster_texts_with_citations

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    doc_id: Optional[str] = None  

@router.post("/query")
async def query_documents(request: QueryRequest):
    """
    Functions:
    It perform a text search query on documents or within a specified document.

    Returns:
        A dictionary with the list of results. Each result contains:
            - document_id
            - extracted_answer
            - citation
    """
    # Searches within a specific document if document_id provided, else search all documents
    if request.doc_id:
        relevant_chunks = search_in_document(request.query, request.doc_id, top_k=15)
    else:
        relevant_chunks = search(request.query, top_k=15)
        
    if not relevant_chunks:
        return {"results": [], "message": "No relevant documents found."}

    docs = {}
    for chunk in relevant_chunks:
        doc = docs.setdefault(chunk['doc_id'], {"answers": [], "citations": []})
        doc["answers"].append(chunk["text"])
        citation = f"Page {chunk.get('page', '?')}, Para {chunk.get('paragraph', '?')}"
        doc["citations"].append(citation)

    results = []
    for doc_id, data in docs.items():
        results.append({
            "doc_id": doc_id,
            "answer": " ".join(data["answers"]).strip(),
            "citation": ", ".join(data["citations"])
        })

    return {"results": results}

@router.get("/themes")
async def get_themes(q: str = Query(..., min_length=3), top_k: int = 20):
    """
    Function:
    Retrieves thematic summaries based on a query provided by the user.

    Returns:
    Contains the original query and a summary of identified themes.
    """
    chunks = search(q, top_k=top_k)
    if not chunks:
        return {"theme_summary": "No relevant documents found."}
    theme_summary = identify_themes(chunks)
    return {
        "query": q,
        "theme_summary": theme_summary
    }

@router.get("/synthesize")
async def synthesize_themes(n_clusters: int = 4):
    """
    Functions:
    Cluster all text chunks and synthesizes thematic summaries with citations.


    Returns:
    Containing synthesized themes, each with an ID, summary, citations, and supporting answers.
    """
    all_chunks = get_all_chunks()
    if not all_chunks:
        return {"error": "No  chunks found."}

    clustered = cluster_texts_with_citations(all_chunks, n_clusters=n_clusters)
    
    themes = []
    for theme_id, chunks in clustered.items():
        result = identify_themes(chunks, theme_id)
        themes.append({
            "theme_id": theme_id,
            "summary": result["summary"],
            "citations": result["citations"],
            "answers": result["answers"]
        })

    return {"themes": themes, "total_themes": len(themes)}
