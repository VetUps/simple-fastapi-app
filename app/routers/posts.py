from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas, oauth2
from typing import List

router = APIRouter(
    prefix="/posts",
    tags=["Tags"] 
    )

@router.get("/", response_model=List[schemas.PostResponseWithVotes])
def get_posts(db: Session = Depends(get_db), limit: int = 5, page: int = 1, search: str = ""):
    posts_to_skip = limit * (page - 1)

    posts = (
        db.query(models.Post, func.count(models.Vote.user_id).label("votes"))
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.post_id)
        .where(models.Post.post_title.contains(search.lower()))
        .group_by(models.Post.post_id)
        .limit(limit=limit)
        .offset(offset=posts_to_skip).all()
    )

    return posts

@router.get("/{id}", response_model=schemas.PostResponseWithVotes)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).where(models.Post.post_id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

    post = (
        db.query(models.Post, func.count(models.Vote.user_id).label("votes"))
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.post_id)
        .where(models.Post.post_id == id)
        .group_by(models.Post.post_id).first()
    )

    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    new_post = models.Post(user_id=current_user.user_id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    deleted_post = db.query(models.Post).where(models.Post.post_id == id).first()

    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

    if deleted_post.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform requested action")

    db.delete(deleted_post, synchronize_session=False)
    db.commit()

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).where(models.Post.post_id == id)
    finded_post = post_query.first()

    if finded_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

    if finded_post.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform requested action")
    
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()

@router.post("/{id}/vote", response_model=schemas.Vote, status_code=status.HTTP_201_CREATED)
def vote_post(id: int,  db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).where(models.Post.post_id == id).first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

    existed_vote = db.query(models.Vote).where(models.Vote.post_id == id, models.Vote.user_id == current_user.user_id).first()

    if existed_vote:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.user_id} already vote on post {id}")

    vote = models.Vote(post_id=id, user_id=current_user.user_id)

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote

@router.delete("/{id}/vote", status_code=status.HTTP_204_NO_CONTENT)
def unvote_post(id: int,  db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).where(models.Post.post_id == id).first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

    existed_vote = db.query(models.Vote).where(models.Vote.post_id == id, models.Vote.user_id == current_user.user_id).first()
    
    if existed_vote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"vote not found")

    db.delete(existed_vote)
    db.commit()
