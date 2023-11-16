from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request

from auth.authentication import MyCustomException
from db import models
from db.database import engine
from router import user
from router import Blog
from auth import authentication
import pandas as pd

app = FastAPI()


# Create a custom exception handler
@app.exception_handler(MyCustomException)
async def custom_exception_handler(request: Request, exc: MyCustomException):
    return JSONResponse(
        content={"error": exc.detail},
        status_code=401
    )


app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(Blog.router)

models.Base.metadata.create_all(engine)
