from httpx import AsyncClient

from custom_types import *

async def test_vote_post(client: AsyncClient, create_user: UserCreator, login_user: TokenCreator, create_post: PostCreator):
    author, clean_password = await create_user()
    token = await login_user(author.user_email, clean_password)
    post = await create_post(author)

    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }

    response = await client.post(f"http://127.0.0.1:8000/posts/{post.post_id}/vote", headers=headers)
    assert response.status_code == 201

async def test_vote_post_twice(client: AsyncClient, create_user: UserCreator, login_user: TokenCreator, create_post: PostCreator, create_vote: VoteCreator):
    author, clean_password = await create_user()
    token = await login_user(author.user_email, clean_password)
    post = await create_post(author)
    await create_vote(author, post)

    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }

    response = await client.post(f"http://127.0.0.1:8000/posts/{post.post_id}/vote", headers=headers)
    assert response.status_code == 409
    