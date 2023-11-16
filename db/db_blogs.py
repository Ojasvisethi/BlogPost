from sqlalchemy.orm import Session

from db.models import DbBlog
from schema import BlogBase
from fastapi import HTTPException, status


# def create_blog(db: Session, request: BlogBase):
#     new_article = DbBlog(
#         title=request.title,
#         content=request.content,
#         user_id=request.creator_id
#     )
#     db.add(new_article)
#     db.commit()
#     db.refresh(new_article)
#     return new_article


def create_blog(db: Session, request: BlogBase):
    new_article = DbBlog(
        title=request.title,
        content=request.content,
        user_id=request.creator_id
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article


def get_all_blogs(db: Session):
    return db.query(DbBlog).all()


def get_blog(db: Session, id: int):
    article = db.query(DbBlog).filter(DbBlog.id == id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Article with id {id} not found')
    return article
