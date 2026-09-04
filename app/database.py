from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f"postgresql+psycopg://postgres:1234@localhost:5432/simple_fastapi_app"
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
