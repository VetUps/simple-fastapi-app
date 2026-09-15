from fastapi import status, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import posts, votes
from app import models, oauth2
from typing import List

from app.services.posts import PostSerivce
from app.services.votes import VoteService
from app.repositories.posts import PostRepository

router = APIRouter(
    prefix="/posts",
    tags=["Tags"] 
    )

@router.get("/test_with_votes", response_model=List[posts.PostResponseWithRealVotes])
async def get_posts_test(db: AsyncSession = Depends(get_db)):
    return await PostRepository.get_with_votes_test(db)

@router.get("/", response_model=List[posts.PostResponseWithVotes])
async def get_posts(db: AsyncSession = Depends(get_db), limit: int = 5, page: int = 1, search: str = ""):
    return await PostSerivce.get_posts(db, limit, page, search)

@router.get("/{id}", response_model=posts.PostResponseWithVotes)
async def get_post(id: int, db: AsyncSession = Depends(get_db)):
    result = await PostSerivce.get_post(db, id)
    return result

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=posts.PostResponse)
async def create_post(post: posts.PostCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return await PostSerivce.create_post(db, post, current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    await PostSerivce.delete_post(db, id, current_user)

@router.put("/{id}", response_model=posts.PostResponse)
async def update_post(id: int, post: posts.PostUpdate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return await PostSerivce.update_post(db, id, post, current_user)

@router.post("/{id}/vote", response_model=votes.Vote, status_code=status.HTTP_201_CREATED)
async def vote_post(id: int,  db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return await VoteService.vote_post(db, id, current_user)

@router.delete("/{id}/vote", status_code=status.HTTP_204_NO_CONTENT)
async def unvote_post(id: int,  db: AsyncSession = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    await VoteService.unvote_post(db, id, current_user)
    