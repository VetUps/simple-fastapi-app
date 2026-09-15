from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

async_eninge = create_async_engine(str(settings.DATABASE_URL), echo=True)

AsyncSession = async_sessionmaker(bind=async_eninge, autoflush=False)

async def get_db():
    async with AsyncSession() as session:
        yield session
