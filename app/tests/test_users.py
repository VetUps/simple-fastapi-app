from httpx import AsyncClient

async def test_create_user_success(client: AsyncClient):
    user_data = {
        "user_email": "user@test.com",
        "user_password": "password"
    }

    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["user_email"] == "user@test.com"

async def test_create_user_duplicate_email(client: AsyncClient):
    user_data = {
        "user_email": "user@test.com",
        "user_password": "password"
    }

    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)
    assert response.status_code == 201

    response = await client.post(url="http://127.0.0.1:8000/users/", json=user_data)
    assert response.status_code == 409
