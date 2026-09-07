from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(str(settings.DATABASE_URL), echo=True)

session_factory = sessionmaker(bind=engine, autoflush=False)

def get_db():
    db = session_factory()

    try:
        yield db
    finally:
        db.close()
