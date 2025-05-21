import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io
import os
from backend.app.services.vector_db import store_text_chunks  

#path to the poppler file 
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"

def extract_text_from_pdf(pdf_path: str):
    """
    Extract  meaningful text from each page of a PDF using OCR.
    Returns a list of dicts: [{"page": page_num, "text": text}, ...]
    """
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    full_text = []
    for page_num, img in enumerate(images, start=1):
        text = pytesseract.image_to_string(img)
        full_text.append({"page": page_num, "text": text})
    return full_text

def extract_text_from_image(image_bytes: bytes):
    """
    Extract text from an image byte stream using OCR.
    Returns a list with a single dict: [{"page": 1, "text": text}]
    """
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img)
    return [{"page": 1, "text": text}]

def chunk_text_pages(pages_text):
    """
    Split page texts into paragraph chunks.
    Input: list of {"page": int, "text": str}
    Output: list of chunks with page and paragraph info
    """
    chunks = []
    for page_data in pages_text:
        page_num = page_data["page"]
        paragraphs = page_data["text"].split("\n\n")  # Split by double newlines for paragraphs
        for para_num, para in enumerate(paragraphs, start=1):
            cleaned_para = para.strip()
            if cleaned_para:
                chunks.append({
                    "page": page_num,
                    "paragraph": para_num,
                    "text": cleaned_para
                })
    return chunks

def process_pdf_and_store(doc_id: str, pdf_path: str, filename: str = ""):
    """
    extract text from PDF, chunk, and store in vector Databsse.
    """
    pages_text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text_pages(pages_text)
    store_text_chunks(doc_id, chunks, filename)
    print(f"Processed and stored {len(chunks)} chunks for document {doc_id}")

def process_image_and_store(doc_id: str, image_bytes: bytes, filename: str = ""):
    """
    Extract text from image bytes, chunk (only one page), and stores it.
    """
    pages_text = extract_text_from_image(image_bytes)
    chunks = chunk_text_pages(pages_text)
    store_text_chunks(doc_id, chunks, filename)
    print(f"Processed and stored {len(chunks)} chunks for image document {doc_id}")
