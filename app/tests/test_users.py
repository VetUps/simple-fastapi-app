from typing import Any

from httpx import AsyncClient
from app.models import User

async def test_create_user_success(client: AsyncClient):
    user_data = {
        "user_email": "user@test.com",
        "user_password": "password"
    }

    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["user_email"] == "user@test.com"

async def test_create_user_with_invalid_email(client: AsyncClient):
    user_data = {
        "user_email": "usertest.com",
        "user_password": "password"
    }

    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)

    assert response.status_code == 422

async def test_create_user_duplicate_email(client: AsyncClient):
    user_data = {
        "user_email": "user@test.com",
        "user_password": "password"
    }

    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)
    assert response.status_code == 201

    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)
    assert response.status_code == 409

async def test_get_non_existent_user(client: AsyncClient):
    user_id = -1

    response = await client.get(url=f"http://127.0.0.1:8000/users/{user_id}")
    assert response.status_code == 404

async def test_get_existing_user(client: AsyncClient):
    user_data = {
            "user_email": "user@test.com",
            "user_password": "password"
        }
    
    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)
    response_data = response.json()
    assert response.status_code == 201
    user_id = response_data["user_id"]

    response = await client.get(url=f"http://127.0.0.1:8000/users/{user_id}")
    response_data = response.json()
    assert response.status_code == 200
    assert user_data["user_email"] == response_data["user_email"]

# TODO: почему то 401 ошибка при логине единственным юзером в БД
async def test_login_user(client: AsyncClient, existed_user):
    user = await existed_user()

    user_data = {
        "grant_type": "password",
        "username": user.user_email,
        "password": user.user_password,
        "scope": "read"
    }
    
    response = await client.post(url="http://127.0.0.1:8000/login", data=user_data)
    response_data = response.json()
    print(response_data)

    assert response.status_code == 200
