from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
import pytest

from app.services.users import UserService

async def test_create_user():
    mock_db = MagicMock()

    raw_password = "123456"
    user_email = "mockeduser@gmail.com"
    user_data = {"user_email": user_email, "user_password": raw_password}

    mock_user = MagicMock()
    mock_user.user_email = user_email
    mock_user.model_dump.return_value = user_data

    with patch("app.services.users.UserRepository.is_exists_by_email", new=AsyncMock(return_value=False)) as mock_is_exists_email, \
        patch("app.services.users.security.hash_password", new=AsyncMock(return_value="hashed_passowrd")) as mock_hash_password, \
        patch("app.services.users.UserRepository.craete", new=AsyncMock(return_value=mock_user)) as mock_create:
        result = await UserService.create_user(mock_db, mock_user)

        assert result == mock_user

        mock_is_exists_email.assert_called_once_with(mock_db, user_email)
        mock_hash_password.assert_called_once_with(raw_password)
        mock_create.assert_called_once_with(mock_db, user_data)

async def test_create_already_existed_user():
    mock_db = MagicMock()

    user_email = "mockeduser@gmail.com"
    user_data = {"user_email": user_email, "user_password": "123456"}

    mock_user = MagicMock()
    mock_user.user_email = user_email
    mock_user.model_dump.return_value = user_data

    with patch("app.services.users.UserRepository.is_exists_by_email", new=AsyncMock(return_value=True)):
        with pytest.raises(HTTPException) as exc_info:
            await UserService.create_user(mock_db, mock_user)

        assert exc_info.value.status_code == 409