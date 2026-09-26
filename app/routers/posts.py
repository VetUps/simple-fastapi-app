from fastapi import status, Depends, APIRouter, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import oauth2
from app.database import get_db
from app.schemas import posts, votes, users
from app.services.posts import PostService
from app.services.votes import VoteService
from app.tasks import send_notification

router = APIRouter(
    prefix="/posts",
    tags=["Posts"] 
    )

CACHE_TTL = 30

@router.get("/", response_model=List[posts.PostWithVotes])
async def get_posts(db: AsyncSession = Depends(get_db), limit: int = 5, page: int = 1, search: str = ""):
    return await PostService.get_posts(db, limit, page, search)

@router.get("/{id}", response_model=posts.PostWithVotes)
async def get_post(id: int, db: AsyncSession = Depends(get_db)):
    result = await PostService.get_post(db, id)
    return result

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=posts.PostWithUser)
async def create_post(post: posts.PostCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: users.UserResponse = Depends(oauth2.get_current_user)):
    result = await PostService.create_post(db, post, current_user)
    # background_tasks.add_task(utils.send_notification, result.post_id, current_user.user_email)
    send_notification.delay(result.post_id, current_user.user_email)
    return result

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: AsyncSession = Depends(get_db), current_user: users.UserResponse = Depends(oauth2.get_current_user)):
    await PostService.delete_post(db, id, current_user)

@router.put("/{id}", response_model=posts.PostWithUser)
async def update_post(id: int, post: posts.PostUpdate, db: AsyncSession = Depends(get_db), current_user: users.UserResponse = Depends(oauth2.get_current_user)):
    result = await PostService.update_post(db, id, post, current_user)
    return result

@router.post("/{id}/vote", response_model=votes.Vote, status_code=status.HTTP_201_CREATED)
async def vote_post(id: int,  db: AsyncSession = Depends(get_db), current_user: users.UserResponse = Depends(oauth2.get_current_user)):
    result = await VoteService.vote_post(db, id, current_user)
    return result

@router.delete("/{id}/vote", status_code=status.HTTP_204_NO_CONTENT)
async def unvote_post(id: int,  db: AsyncSession = Depends(get_db), current_user: users.UserResponse = Depends(oauth2.get_current_user)): 
    await VoteService.unvote_post(db, id, current_user)
    