from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    user_email: EmailStr
    user_password: str

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    pass

class UserResponse(BaseModel):
    user_email: EmailStr
    user_created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    user_email: EmailStr

class PostBase(BaseModel):
    post_title: str
    post_content: str
    post_published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    user: UserResponse
    post_created_at: datetime