"""
The main file which executes the programs and loads all the necessary files

"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.api import upload, query
from app.api.documents import router as documents_router
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "static"))

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")   #loading of all the static files (html , css and js)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(documents_router, prefix="/api", tags=["documents"])

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_PATH, "index.html"))
