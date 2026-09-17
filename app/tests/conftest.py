import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.models import Base
from app.main import app

async_enige = create_async_engine(url=str(settings.TEST_DATABASE_URL))
AsyncSessionFactory = async_sessionmaker(bind=async_enige, autoflush=False, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with async_enige.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with async_enige.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_enige.dispose()       

@pytest.fixture
async def client():
    transport = ASGITransport(app)

    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
        