from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.db import init_db
from routers.quiz import quiz_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(quiz_router)


@app.get("/")
def root():
    return {"about": "Multiplayer Quiz Backend", "author": "Sheikh Rashdan"}
