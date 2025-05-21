import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# API keys and paths loaded from environment variables 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploaded_docs")
VECTOR_INDEX_DIR = os.getenv("VECTOR_INDEX_DIR", "data/vector_index")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_INDEX_DIR, exist_ok=True)
