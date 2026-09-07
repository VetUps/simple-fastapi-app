from fastapi import FastAPI

from app.routers import posts, users, auth
from app.database import engine
from app import models

app = FastAPI()
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {
        "message": "Hello World!"
    }
