# backend/app/init_db.py

from app.core.db import engine
from app.core.db import Base  # ✅ This is where Base is defined
from app.models.document import Document  # Import your model so it's registered

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized.")

if __name__ == "__main__":
    init_db()
