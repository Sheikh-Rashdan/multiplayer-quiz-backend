from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"about": "Multiplayer Quiz Backend", "author": "Sheikh Rashdan"}
