from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"about": "Multiplayer Quiz Backend", "author": "Sheikh Rashdan"}
