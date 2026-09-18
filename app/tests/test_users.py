from httpx import AsyncClient

from custom_types import *

async def test_create_user_success(client: AsyncClient):
    user_data = {
        "user_email": "user@test.com",
        "user_password": "password"
    }

    response = await client.post(url="/users/", json=user_data)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["user_email"] == "user@test.com"

async def test_create_user_with_invalid_email(client: AsyncClient):
    user_data = {
        "user_email": "usertest.com",
        "user_password": "password"
    }

    response = await client.post(url="/users/", json=user_data)

    assert response.status_code == 422

async def test_create_user_duplicate_email(client: AsyncClient):
    user_data = {
        "user_email": "user@test.com",
        "user_password": "password"
    }

    response = await client.post(url="/users/", json=user_data)
    assert response.status_code == 201

    response = await client.post(url="/users/", json=user_data)
    assert response.status_code == 409

async def test_get_non_existent_user(client: AsyncClient):
    user_id = -1

    response = await client.get(url=f"/users/{user_id}")
    assert response.status_code == 404

async def test_get_existing_user(client: AsyncClient):
    user_data = {
            "user_email": "user@test.com",
            "user_password": "password"
        }
    
    response = await client.post(url="/users/", json=user_data)
    response_data = response.json()
    assert response.status_code == 201
    user_id = response_data["user_id"]

    response = await client.get(url=f"/users/{user_id}")
    response_data = response.json()
    assert response.status_code == 200
    assert user_data["user_email"] == response_data["user_email"]

async def test_login_user(client: AsyncClient, create_user: UserCreator):
    user, clean_password = await create_user()
    user_login_data = {
        "grant_type": "password",
        "username": user.user_email,
        "password": clean_password,
        "scope": "read"
    }
    
    response = await client.post(url="/login", data=user_login_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data.keys()
    assert "token_type" in response_data.keys()

async def test_login_user_invalid_password(client: AsyncClient, create_user: UserCreator):
    user, _ = await create_user()
    user_login_data = {
        "grant_type": "password",
        "username": user.user_email,
        "password": "invalid password",
        "scope": "read"
    }
    
    response = await client.post(url="/login", data=user_login_data)
    assert response.status_code == 401

async def test_login_user_invalid_email(client: AsyncClient, create_user: UserCreator):
    _, clean_password = await create_user()
    user_login_data = {
        "grant_type": "password",
        "username": "invalid email",
        "password": clean_password,
        "scope": "read"
    }
    
    response = await client.post(url="/login", data=user_login_data)
    assert response.status_code == 401
