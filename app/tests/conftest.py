import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.models import Base
from app.main import app
from app.database import get_db
from app.services.users import UserService
from app.schemas import users

async_enige = create_async_engine(url=str(settings.TEST_DATABASE_URL))
AsyncSessionFactory = async_sessionmaker(bind=async_enige, autoflush=False, expire_on_commit=False)

# Override зависимостей FastAPI
async def get_test_db():
    async with AsyncSessionFactory() as session:
        yield session

@pytest.fixture(autouse=True)
def override_get_db():
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)

# Основные фикстуры
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with async_enige.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with async_enige.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_enige.dispose()           

@pytest.fixture(scope="function", autouse=True)
async def clear_tables():
    async with AsyncSessionFactory() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())

        await session.commit()

@pytest.fixture
async def client():
    transport = ASGITransport(app)

    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

@pytest.fixture
async def existed_user():
    async def create_user():
        async with AsyncSessionFactory() as session:
            user_data = {
                "user_email": "test@gmail.com",
                "user_password": "123456"
            }
            user_create = users.UserCreate(**user_data)
        
            res = await UserService.create_user(session, user_create)
            return res

    return create_user
    