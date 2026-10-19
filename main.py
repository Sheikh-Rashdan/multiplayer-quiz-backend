from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.db import init_db
from routers.question import question_router
from routers.quiz import quiz_router
from routers.room import room_router
from routers.user import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(quiz_router)
app.include_router(question_router)
app.include_router(room_router)


@app.get("/")
def root():
    return {"about": "Multiplayer Quiz Backend", "author": "Sheikh Rashdan"}
