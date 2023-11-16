from fastapi import APIRouter, Depends , HTTPException ,status
from typing import List

from sqlalchemy.orm import Session

from auth.oauth2 import oauth2_scheme, get_current_user
from db import db_blogs
from db.database import get_db
from schema import BlogDisplay, BlogBase, UserBase, BlogUserDisplay

router = APIRouter(prefix="/blogs", tags=["blogs"])


@router.post('/', response_model=BlogDisplay)
def create_blog(request: BlogBase, db: Session = Depends(get_db) , current_user: UserBase = Depends(get_current_user)):
    if not current_user.Admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'You are not Authorizec to create a Blog')
    art = db_blogs.create_blog(db, request)
    return art


@router.get("/all", response_model=List[BlogDisplay])
def get_all_blogs(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return db_blogs.get_all_blogs(db)


@router.get('/{id}', response_model=BlogUserDisplay)
def get_article(id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return {
        'data': db_blogs.get_blog(db, id),
        'current_user': current_user
    }
