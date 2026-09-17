import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.models import Base

async_enige = create_async_engine(url=str(settings.TEST_DATABASE_URL))
AsyncSessionFactory = async_sessionmaker(bind=async_enige, autoflush=False, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def get_test_db():
    async with async_enige.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with async_enige.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_enige.dispose()       
