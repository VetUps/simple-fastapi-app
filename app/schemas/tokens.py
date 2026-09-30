from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

from schemas import users

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class AccessTokenData(BaseModel):
    user_id: int
    user_email: EmailStr

class RefreshToken(BaseModel):
    token_id: int
    token_hash: str
    user_id: int
    expires_at: datetime
    is_revoked: bool

    model_config = ConfigDict(from_attributes=True)

class RefreshTokenWithUser(RefreshToken):
    user: users.UserResponse
    