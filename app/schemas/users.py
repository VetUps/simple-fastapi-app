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
    user_id: int
    user_email: EmailStr
    user_created_at: datetime

    model_config = ConfigDict(from_attributes=True)