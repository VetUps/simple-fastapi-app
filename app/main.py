from fastapi import FastAPI
from .routers import posts, users
from .database import engine
from . import models

app = FastAPI()
app.include_router(posts.router)
app.include_router(users.router)

models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {
        "message": "Hello World!"
    }
