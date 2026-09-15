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

class PostResponse(PostBase):
    post_id: int
    post_created_at: datetime
    user: UserResponse

class PostResponseWithVotes(BaseModel):
    Post: PostResponse
    votes: int

class PostResponseWithRealVotes(BaseModel):
    post_id: int
    user: UserResponse
    post_created_at: datetime
    votes: List[Vote]

class UserResponseWithPosts(BaseModel):
    user_email: EmailStr
    user_created_at: datetime
    posts: List[PostBase]
