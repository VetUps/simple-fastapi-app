import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from app.models import Base, User, Post, Vote
from app.main import app
from app.database import get_db
from app.services.users import UserService
from app.services.posts import PostService
from app.services.votes import VoteService
from app.schemas import users, tokens, posts

from custom_types import UserCreator, PostCreator, VoteCreator, TokenCreator

async_engine = create_async_engine(url=str(settings.TEST_DATABASE_URL))
AsyncSessionFactory = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)

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
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()           

@pytest.fixture(scope="function", autouse=True)
async def clear_tables():
    yield
    async with AsyncSessionFactory() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())

        await session.commit()

@pytest.fixture
async def client():
    transport = ASGITransport(app)

    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as async_client:
        yield async_client

@pytest.fixture
async def create_user() -> UserCreator:
    async def _create_user(email: str = "test@gmail.com", password: str = "123456") -> tuple[User, str]:
        async with AsyncSessionFactory() as session:
            user_data = {
                "user_email": email,
                "user_password": password
                }
            user_create = users.UserCreate(**user_data)
            user_model = await UserService.create_user(session, user_create)

            return user_model, password
    return _create_user

@pytest.fixture
async def login_user(client: AsyncClient) -> TokenCreator:
    async def _login_user(email: str, password: str) -> tokens.Token:
        user_login_data = {
                "grant_type": "password",
                "username": email,
                "password": password,
                "scope": "read"
            }

        response = await client.post("/login", data=user_login_data)
        response_data = response.json()
        
        return tokens.Token(**response_data)
    return _login_user

@pytest.fixture
async def create_post() -> PostCreator:
    async def _create_post(author: User, title: str = "New post", content: str = "Post content") -> Post:
        async with AsyncSessionFactory() as session:
            post_data = {
                "post_title": title,
                "post_content": content
            }
            post_create = posts.PostCreate(**post_data, post_published=True)
            post_model = await PostService.create_post(session, post_create, author)

            return post_model
    return _create_post 

@pytest.fixture
async def create_vote() -> VoteCreator:
    async def _create_vote(author: User, post: Post) -> Vote:
        async with AsyncSessionFactory() as session:
            vote = await VoteService.vote_post(session, post.post_id, author)
            return vote
    return _create_vote 