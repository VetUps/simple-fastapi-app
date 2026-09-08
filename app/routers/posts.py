from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func, select, text, update
from app.database import get_db
from app import models, schemas, oauth2
from app.repositories import posts
from typing import List

from app.services.posts import PostSerivce
from app.services.votes import VoteService

router = APIRouter(
    prefix="/posts",
    tags=["Tags"] 
    )

@router.get("/", response_model=List[schemas.PostResponseWithVotes])
def get_posts(db: Session = Depends(get_db), limit: int = 5, page: int = 1, search: str = ""):
    return PostSerivce.get_posts(db, limit, page, search)

@router.get("/{id}", response_model=schemas.PostResponseWithVotes)
def get_post(id: int, db: Session = Depends(get_db)):
    return PostSerivce.get_post(db, id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return PostSerivce.create_post(db, post, current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    PostSerivce.delete_post(db, id, current_user)

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return PostSerivce.update_post(db, id, post, current_user)

@router.post("/{id}/vote", response_model=schemas.Vote, status_code=status.HTTP_201_CREATED)
def vote_post(id: int,  db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return VoteService.vote_post(db, id, current_user)

@router.delete("/{id}/vote", status_code=status.HTTP_204_NO_CONTENT)
def unvote_post(id: int,  db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    VoteService.unvote_post(db, id, current_user)