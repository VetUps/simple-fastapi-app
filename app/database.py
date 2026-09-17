from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

async_eninge = create_async_engine(str(settings.DATABASE_URL), echo=True)

AsyncSessionFactory = async_sessionmaker(bind=async_eninge, autoflush=False, expire_on_commit=False)

async def get_db():
    async with AsyncSessionFactory() as session:
        yield session
