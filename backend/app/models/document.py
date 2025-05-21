from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.db import Base 

class Document(Base):
    """
    SQLAlchemy ORM model representing a document record in the database.
    It is the format in which the document will be stored

    Attributes:
        id (int)
        doc_id (str)
        filename (str)
        file_path (str)
        extracted_text (str)
        page_count (int)
        chunk_count (int)
        upload_time (datetime)
    """

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=False)

    page_count = Column(Integer, nullable=False)       
    chunk_count = Column(Integer, nullable=False)      
    upload_time = Column(DateTime, default=datetime.utcnow)  
