from fastapi import status, Depends, APIRouter, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app import models, oauth2, utils
from app.database import get_db
from app.schemas import posts, votes
from app.services.posts import PostService
from app.services.votes import VoteService
from app.repositories.posts import PostRepository

router = APIRouter(
    prefix="/posts",
    tags=["Posts"] 
    )

@router.get("/test_with_votes", response_model=List[posts.PostResponseWithRealVotes])
async def get_posts_test(db: AsyncSession = Depends(get_db)):
    return await PostRepository.get_with_votes_test(db)

@router.get("/", response_model=List[posts.PostResponseWithVotes])
async def get_posts(db: AsyncSession = Depends(get_db), limit: int = 5, page: int = 1, search: str = ""):
    return await PostService.get_posts(db, limit, page, search)

@router.get("/{id}", response_model=posts.PostResponseWithVotes)
async def get_post(id: int, db: AsyncSession = Depends(get_db)):
    result = await PostService.get_post(db, id)
    return result

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=posts.PostResponse)
async def create_post(post: posts.PostCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    result = await PostService.create_post(db, post, current_user)
    background_tasks.add_task(utils.send_notification, result.post_id, current_user.user_email)
    return result

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    await PostService.delete_post(db, id, current_user)

@router.put("/{id}", response_model=posts.PostResponse)
async def update_post(id: int, post: posts.PostUpdate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return await PostService.update_post(db, id, post, current_user)

@router.post("/{id}/vote", response_model=votes.Vote, status_code=status.HTTP_201_CREATED)
async def vote_post(id: int,  db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return await VoteService.vote_post(db, id, current_user)

@router.delete("/{id}/vote", status_code=status.HTTP_204_NO_CONTENT)
async def unvote_post(id: int,  db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    await VoteService.unvote_post(db, id, current_user)
    