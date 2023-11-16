from pydantic import BaseModel
from typing import List


class UserBase(BaseModel):
    username: str
    email: str
    password: str


class UserBase2(BaseModel):
    username: str
    email: str

class Blog(BaseModel):
    title: str
    content: str
    published: bool

    class Config():
        orm_mode = True


class UserDisplay(BaseModel):
    username: str
    email: str
    items: List[Blog] = []

    class Config():
        orm_mode = True


class User(BaseModel):
    id: int
    username: str

    class Config():
        orm_mode = True


class BlogDisplay(BaseModel):
    title: str
    content: str
    user_id: int

    class Config():
        orm_mode = True


class BlogUserDisplay(BaseModel):
    data: BlogDisplay
    current_user: UserBase2

    class Config():
        orm_mode = True


class BlogBase(BaseModel):
    title: str
    content: str
    creator_id: int
