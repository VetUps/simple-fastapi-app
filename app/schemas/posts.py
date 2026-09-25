from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List

from app.schemas.users import UserResponse
from app.schemas.votes import Vote

class PostBase(BaseModel):
    post_title: str
    post_content: str
    post_published: bool = True

    model_config = ConfigDict(from_attributes=True)

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostWithUser(PostBase):
    post_id: int
    post_created_at: datetime
    user: UserResponse

class PostWithoutUser(PostBase):
    post_id: int
    post_created_at: datetime

class PostWithVotes(BaseModel):
    Post: PostWithUser
    votes: int

    model_config = ConfigDict(from_attributes=True)

class PostResponseWithRealVotes(BaseModel):
    post_id: int
    user: UserResponse
    post_created_at: datetime
    votes: List[Vote]

class UserWithPosts(BaseModel):
    user_email: EmailStr
    user_created_at: datetime
    posts: List[PostBase]

    model_config = ConfigDict(from_attributes=True)