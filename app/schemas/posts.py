from pydantic import BaseModel
from datetime import datetime
from typing import List

from app.schemas.users import UserResponse
from app.schemas.votes import Vote

class PostBase(BaseModel):
    post_title: str
    post_content: str
    post_published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    post_id: int
    user: UserResponse
    post_created_at: datetime

class PostResponseWithVotes(BaseModel):
    Post: PostResponse
    votes: int

class PostResponseWithRealVotes(BaseModel):
    post_id: int
    user: UserResponse
    post_created_at: datetime
    votes: List[Vote]