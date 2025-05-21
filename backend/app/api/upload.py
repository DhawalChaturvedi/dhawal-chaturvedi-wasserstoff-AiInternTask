import os
from uuid import uuid4
from datetime import datetime
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.core.db import get_db
from app.models.document import Document
from app.services.ocr import extract_text_from_pdf, extract_text_from_image
from app.services.vector_db import store_text_chunks

router = APIRouter()              

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    It is an endpoint to upload multiple documents (PDFs or images), perform OCR, chunk the extracted text,
    store text chunks in a vector database, and save metadata in a relational database.


    Raises:
        HTTPException: If no files are uploaded or no valid files are found.

    Returns:
        dict: Summary of uploaded documents including their IDs, filenames, and chunk counts.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    uploaded_docs = []

    for file in files:
        ext = file.filename.split('.')[-1].lower()
        # only pdf , png , jpg or jpeg type files are allowed
        if ext not in ["pdf", "png", "jpg", "jpeg"]:
            continue  # Skip unsupported file types

        # Generates a unique document ID to every document
        doc_id = f"DOC{str(uuid4())[:8].upper()}"
        save_path = os.path.join(UPLOAD_DIR, f"{doc_id}.{ext}")

        # Save the uploaded file to disk
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)

        # Perform OCR extraction depending on file type
        if ext == "pdf":
            pages_text = extract_text_from_pdf(save_path)
        else:
            pages_text = extract_text_from_image(contents)

        # Split extracted text into paragraph-level chunks with page and paragraph info
        chunks = []
        for pages in pages_text:
            for i, para in enumerate(pages["text"].split('\n\n')):
                para = para.strip()
                if para:
                    chunks.append({
                        "page": pages.get("page", 1),
                        "paragraph": i + 1,
                        "text": para
                    })

        # Storing the chunks in the vector database 
        store_text_chunks(doc_id, chunks, filename=file.filename)

        # Create a new Document record in the relational database to store it
        new_doc = Document(
            doc_id=doc_id,
            filename=file.filename,
            file_path=save_path,
            extracted_text="\n".join([p["text"] for p in pages_text]),
            page_count=len(pages_text),
            chunk_count=len(chunks),
            upload_time=datetime.utcnow()
        )

        db.add(new_doc)
        uploaded_docs.append({
            "document_id": doc_id,
            "filename": file.filename,
            "chunks_count": len(chunks)
        })

    if not uploaded_docs:
        raise HTTPException(status_code=400, detail="No valid files uploaded.")

    db.commit()  # Commit after all valid documents are added
    return {"uploaded_documents": uploaded_docs}
