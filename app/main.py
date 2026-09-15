from fastapi import FastAPI

from app.routers import posts, users, auth
from app.database import async_eninge
from app import models

app = FastAPI()
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "message": "Hello World!"
    }

@app.get("/create_db")
async def create_db():
    async with async_eninge.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)