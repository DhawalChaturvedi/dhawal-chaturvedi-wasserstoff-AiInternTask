# backend/app/api/documents.py
from fastapi import APIRouter
from app.services.vector_db import metadata  # your metadata list

router = APIRouter()

@router.get("/documents")
async def get_uploaded_documents():
    """
    Functions:
    Retrieve a list of unique uploaded documents.
    
    Returns:
    A list of dictionaries, each containing 'id' and 'name' keys for documents.
    """
    documents = {}
    for item in metadata:
        document_id = item.get("doc_id")
        if document_id and document_id not in documents:
            documents[document_id] = {
                "id": document_id,                       # Document identifier
                "name": item.get("filename", "Unknown")  # Document filename or 'Unknown' if missing
            }
    return list(documents.values())
