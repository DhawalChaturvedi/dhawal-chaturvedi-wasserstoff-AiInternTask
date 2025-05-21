
import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from app.config import VECTOR_INDEX_DIR

os.makedirs(VECTOR_INDEX_DIR, exist_ok=True)

# Initialize sentence transformer model and get embedding dimension
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_dim = embedding_model.get_sentence_embedding_dimension()

# Define paths for FAISS index and metadata storage
index_path = os.path.join(VECTOR_INDEX_DIR, "faiss.index")
metadata_path = os.path.join(VECTOR_INDEX_DIR, "metadata.json")

# Load existing FAISS index or create a new one if not present
if os.path.exists(index_path):
    index = faiss.read_index(index_path)
else:
    index = faiss.IndexFlatL2(embedding_dim)

# Load metadata from JSON file or initialize empty list if file doesn't exist
if os.path.exists(metadata_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
else:
    metadata = []

def save_index():
    """Persist the FAISS index to disk."""
    faiss.write_index(index, index_path)

def save_metadata():
    """Persist the metadata list to disk as JSON."""
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def reset_index_and_metadata():
    """
    Reset both FAISS index and metadata by clearing all stored vectors and metadata.
    """
    global index, metadata
    index = faiss.IndexFlatL2(embedding_dim)
    metadata = []
    save_index()
    save_metadata()
    print("Reset FAISS index and metadata.")

def store_text_chunks(doc_id: str, chunks: list, filename: str = ""):
    """
    Function :
    Encode and store text chunks into the FAISS index along with their metadata.

    """
    for chunk in chunks:
        text = chunk["text"]
        emb = embedding_model.encode(text)
        vec = np.array(emb, dtype=np.float32).reshape(1, -1)
        index.add(vec)
        metadata.append({
            "doc_id": doc_id,
            "filename": filename,
            "page": chunk.get("page", None),
            "paragraph": chunk.get("paragraph", None),
            "text": text
        })
    save_index()
    save_metadata()
    print(f"Stored {len(chunks)} chunks for doc_id {doc_id}")

def search(query: str, top_k=5):
    """
    Functions :
    Search the FAISS index for top_k most similar text chunks to the query.

    Returns:
        List of metadata dicts for the top matching chunks.
    """
    print(f"FAISS index ntotal: {index.ntotal}, metadata length: {len(metadata)}")
    emb = embedding_model.encode(query)
    vec = np.array(emb, dtype=np.float32).reshape(1, -1)
    D, I = index.search(vec, top_k)
    results = []
    for idx in I[0]:
        if idx == -1:
            # No more results
            continue
        if idx < len(metadata):
            results.append(metadata[idx])
        else:
            print(f"Warning: idx {idx} out of range for metadata length {len(metadata)}")
    return results

def search_in_document(query: str, doc_id: str, top_k=5):
    """
    Functions:
    Search for relevant text chunks within a specific document.

    Returns:
    List of metadata dicts for top matching chunks within the document.
    """
    print(f"Search in document: {doc_id}")
    emb = embedding_model.encode(query)
    vec = np.array(emb, dtype=np.float32).reshape(1, -1)
    # Retrieve more candidates than needed to filter by doc_id later
    D, I = index.search(vec, top_k * 5)  
    results = []
    for idx in I[0]:
        if idx == -1:
            continue
        if idx >= len(metadata):
            print(f"Warning: idx {idx} out of range for metadata length {len(metadata)}")
            continue
        meta = metadata[idx]
        if meta.get("doc_id") == doc_id:
            results.append(meta)
            if len(results) >= top_k:
                break
    return results

def get_all_chunks():
    """
    Retrieve all stored text chunk metadata.

    Returns:
        list: All metadata dicts currently stored.
    """
    return metadata
