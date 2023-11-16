from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db import db_user
from db.database import get_db
from schema import UserBase, UserDisplay

router = APIRouter(prefix="/user", tags=["user"])


@router.post('/', response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)


@router.get('/all', response_model=List[UserDisplay])
def get_users(db: Session = Depends(get_db)):
    return db_user.get_all_users(db)


@router.delete("/delete/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    return db_user.delete_user(db, id)


@router.post("/update/{id}")
def update_user(id: int, db: Session = Depends(get_db)):
    return db_user.update_user(db, id)
