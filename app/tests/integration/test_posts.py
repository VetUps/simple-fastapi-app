from httpx import AsyncClient

from custom_types import *

async def test_create_post_success(client: AsyncClient, create_user: UserCreator, login_user: TokenCreator):
    user, clean_password = await create_user()
    token = await login_user(user.user_email, clean_password)

    post_data = {
        "post_title": "new post",
        "post_content": "post text",
    }
    headers = {
        "Authorization": f"Bearer {token.access_token}" # после Bearer не ставить ":" (долго не понимал чё не так)
    }

    response = await client.post("http://127.0.0.1:8000/posts/", json=post_data, headers=headers)
    assert response.status_code == 201

async def test_create_post_without_token(client: AsyncClient):
    post_data = {
        "post_title": "new post",
        "post_content": "post text",
    }

    response = await client.post("http://127.0.0.1:8000/posts/", json=post_data)
    assert response.status_code == 401

async def test_get_posts(client: AsyncClient):
    response = await client.get("http://127.0.0.1:8000/posts/")
    reponse_data = response.json()

    assert response.status_code == 200
    assert isinstance(reponse_data, list)

async def test_get_existing_post(client: AsyncClient, create_user: UserCreator, create_post: PostCreator):
    user, clean_password = await create_user()
    post = await create_post(user)
    response = await client.get(f"http://127.0.0.1:8000/posts/{post.post_id}")
    reponse_data = response.json()

    assert response.status_code == 200
    assert "Post" in reponse_data.keys()
    assert "votes" in reponse_data.keys()

async def test_get_non_existent_post(client: AsyncClient):
    post_id = -1
    response = await client.get(f"http://127.0.0.1:8000/posts/{post_id}")

    assert response.status_code == 404

async def test_update_post_by_author(client: AsyncClient, create_user: UserCreator, login_user: TokenCreator, create_post: PostCreator):
    user, clean_password = await create_user()
    token = await login_user(user.user_email, clean_password)
    post = await create_post(user)

    new_post_data = {
        "post_title": "Updated post title",
        "post_content": "Updated post content"
    }
    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }

    response = await client.put(f"http://127.0.0.1:8000/posts/{post.post_id}", json=new_post_data, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["post_title"] == new_post_data["post_title"]
    assert response_data["post_content"] == new_post_data["post_content"]

async def test_update_post_by_stranger(client: AsyncClient, create_user: UserCreator, login_user: TokenCreator, create_post: PostCreator):
    author, _ = await create_user()
    stranger, clean_password = await create_user("stranger@gmail.com", "123456")
    token = await login_user(stranger.user_email, clean_password)
    post = await create_post(author)

    new_post_data = {
        "post_title": "Updated post title",
        "post_content": "Updated post content"
    }
    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }

    response = await client.put(f"http://127.0.0.1:8000/posts/{post.post_id}", json=new_post_data, headers=headers)
    assert response.status_code == 403

async def test_delete_post_by_author(client: AsyncClient, create_user: UserCreator, login_user: TokenCreator, create_post: PostCreator):
    user, clean_password = await create_user()
    token = await login_user(user.user_email, clean_password)
    post = await create_post(user)

    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }

    response = await client.delete(f"http://127.0.0.1:8000/posts/{post.post_id}", headers=headers)
    assert response.status_code == 204

async def test_delete_post_by_stranger(client: AsyncClient, create_user: UserCreator, login_user: TokenCreator, create_post: PostCreator):
    author, _ = await create_user()
    stranger, clean_password = await create_user("stranger@gmail.com", "123456")
    token = await login_user(stranger.user_email, clean_password)
    post = await create_post(author)

    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }

    response = await client.delete(f"http://127.0.0.1:8000/posts/{post.post_id}", headers=headers)
    assert response.status_code == 403
