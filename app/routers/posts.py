from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, oauth2
from typing import List

from app.services.posts import PostSerivce
from app.services.votes import VoteService
from app.repositories.posts import PostRepository

router = APIRouter(
    prefix="/posts",
    tags=["Tags"] 
    )

@router.get("/test_with_votes", response_model=List[schemas.posts.PostResponseWithRealVotes])
def get_posts_test(db: Session = Depends(get_db)):
    return PostRepository.get_with_votes_test(db)

@router.get("/", response_model=List[schemas.posts.PostResponseWithVotes])
def get_posts(db: Session = Depends(get_db), limit: int = 5, page: int = 1, search: str = ""):
    return PostSerivce.get_posts(db, limit, page, search)

@router.get("/{id}", response_model=schemas.posts.PostResponseWithVotes)
def get_post(id: int, db: Session = Depends(get_db)):
    return PostSerivce.get_post(db, id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.posts.PostResponse)
def create_post(post: schemas.posts.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return PostSerivce.create_post(db, post, current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    PostSerivce.delete_post(db, id, current_user)

@router.put("/{id}", response_model=schemas.posts.PostResponse)
def update_post(id: int, post: schemas.posts.PostUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return PostSerivce.update_post(db, id, post, current_user)

@router.post("/{id}/vote", response_model=schemas.votes.Vote, status_code=status.HTTP_201_CREATED)
def vote_post(id: int,  db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return VoteService.vote_post(db, id, current_user)

@router.delete("/{id}/vote", status_code=status.HTTP_204_NO_CONTENT)
def unvote_post(id: int,  db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    VoteService.unvote_post(db, id, current_user)