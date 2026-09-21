from unittest.mock import patch, Mock, MagicMock, AsyncMock
from fastapi import HTTPException
import pytest

from app.services.posts import PostService

async def test_update_post():
    mock_db = MagicMock()

    post_id = 1
    current_user_id = 1
    post_data = {
        "post_title": "mock title",
        "post_content": "mock content",
    }

    mock_post_new = MagicMock()
    mock_post_new.model_dump.return_value = post_data

    mock_post_to_update = MagicMock()
    mock_post_to_update.user_id = current_user_id

    mock_current_user = MagicMock()
    mock_current_user.user_id = current_user_id

    with patch("app.services.posts.PostRepository.get_by_id", new=AsyncMock(return_value=mock_post_to_update)) as mock_get_by_id, \
         patch("app.services.posts.PostRepository.update", new=AsyncMock(return_value=mock_post_new)) as mock_update:

         result = await PostService.update_post(mock_db, post_id, mock_post_new, mock_current_user)

         assert result == mock_post_new

         mock_get_by_id.assert_called_once_with(mock_db, post_id)
         mock_update.assert_called_once_with(mock_db, post_data, post_id)

async def test_update_non_existent_post():
    mock_db = MagicMock()

    post_id = 1

    mock_post_new = MagicMock()
    mock_current_user = MagicMock()

    with patch("app.services.posts.PostRepository.get_by_id", new=AsyncMock(return_value=None)) as mock_get_by_id:
        with pytest.raises(HTTPException) as exc_info:
            await PostService.update_post(mock_db, post_id, mock_post_new, mock_current_user)

        assert exc_info.value.status_code == 404
        mock_get_by_id.assert_called_once_with(mock_db, post_id)

async def test_update_post_by_stranger():
    mock_db = MagicMock()

    post_id = 1
    current_user_id = 1
    actually_user_id = 2

    mock_post_new = MagicMock()

    mock_post_to_update = MagicMock()
    mock_post_to_update.user_id = actually_user_id

    mock_current_user = MagicMock()
    mock_current_user.user_id = current_user_id

    with patch("app.services.posts.PostRepository.get_by_id", new=AsyncMock(return_value=mock_post_to_update)) as mock_get_by_id:
        with pytest.raises(HTTPException) as exc_info:
            await PostService.update_post(mock_db, post_id, mock_post_new, mock_current_user)

        assert exc_info.value.status_code == 403
        mock_get_by_id.assert_called_once_with(mock_db, post_id)
