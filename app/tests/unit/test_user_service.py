from unittest.mock import patch, Mock, MagicMock, AsyncMock
from fastapi import HTTPException
import pytest

from app.services.users import UserService

async def test_create_user():
    mock_db = MagicMock()

    raw_password = "123456"
    mock_user = MagicMock()
    mock_user.user_email = "mockeduser@gmail.com"
    mock_user.model_dump.return_value = {"user_email": "mockeduser@gmail.com", "user_password": raw_password}

    with patch("app.services.users.UserRepository.get_by_email", new=AsyncMock(return_value=None)) as mock_get_by_email, \
         patch("app.services.users.security.hash_password", new=AsyncMock(return_value="hashed_passowrd")) as mock_hash_password, \
         patch("app.services.users.UserRepository.craete", new=AsyncMock(return_value=mock_user)) as mock_create:
        result = await UserService.create_user(mock_db, mock_user)

        assert result == mock_user

        mock_get_by_email.assert_called_once_with(mock_db, "mockeduser@gmail.com")
        mock_hash_password.assert_called_once_with(raw_password)
        mock_create.assert_called_once_with(mock_db, {"user_email": "mockeduser@gmail.com", "user_password": "hashed_passowrd"})

async def test_create_already_existed_user():
    mock_db = MagicMock()

    mock_user_data = {"user_email": "mockeduser@gmail.com", "user_password": "123456"}
    mock_user = MagicMock()
    mock_user.user_email = "mockeduser@gmail.com"
    mock_user.model_dump.return_value = mock_user_data

    with patch("app.services.users.UserRepository.get_by_email", new=AsyncMock(return_value=mock_user_data)):
        with pytest.raises(HTTPException) as exc_info:
            await UserService.create_user(mock_db, mock_user)

        assert exc_info.value.status_code == 409