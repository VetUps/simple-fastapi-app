from sqlalchemy import select, delete, update, insert, func
from sqlalchemy.orm import Session, joinedload

from app import models

class PostRepository:
    @staticmethod
    def get_many(db: Session, limit: int = 5, offset: int = 0, search: str = ""):
        """
        Возвращает пагинированные посты
        """ 

        query = (
            select(models.Post, func.count(models.Vote.user_id).label("votes"))
            .outerjoin(models.Vote, models.Post.post_id  == models.Vote.post_id)
            .where(models.Post.post_title.contains(search))
            .group_by(models.Post.post_id)
            .limit(limit)
            .offset(offset)
        )

        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = db.execute(query).all()

        return result

    @staticmethod
    def get_by_id(db: Session, post_id: int):
        """
        Возвращает пост по post_id
        """

        query = (
            select(models.Post)
            .where(models.Post.post_id == post_id)
        )
        result = db.execute(query).scalar_one_or_none()

        return result
    
    @staticmethod
    def get_by_id_with_votes(db: Session, post_id: int):
        """
        Возвращает пост по post_id
        """

        query = (
            select(models.Post, func.count(models.Vote.user_id).label("votes"))
            .outerjoin(models.Vote, models.Post.post_id == models.Vote.post_id)
            .where(models.Post.post_id == post_id)
            .group_by(models.Post.post_id)
        )
        result = db.execute(query).one_or_none()

        return result

    @staticmethod
    def create(db: Session, post_data: dict):
        """
        Создаёт новый пост
        """

        new_post = models.Post(**post_data)

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return new_post

    @staticmethod
    def delete(db: Session, post_id: int):
        """
        Удаляет пост
        """
        stmt = (
            delete(models.Post)
            .where(models.Post.post_id == post_id)
        )

        db.execute(stmt)
        db.commit()

    @staticmethod
    def update(db: Session, post_data: dict, post_id: int):
        """
        Обновляет существующий пост
        """
        stmt = (
            update(models.Post)
            .values(**post_data)
            .where(models.Post.post_id == post_id)
            .returning(models.Post)
        )

        result = db.execute(stmt).scalar_one_or_none()
        db.commit()

        return result

    @staticmethod
    def get_with_votes_test(db: Session):
        query = (
            select(models.Post)
            .options(joinedload(models.Post.votes))
        )

        result = db.execute(query).unique().scalars().all()
        print(result)

        return result
