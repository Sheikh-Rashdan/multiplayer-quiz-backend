from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import storage.user as storage
from database.db import get_db
from database.models import User
from models.user import AccessToken, UserCredentials, UserModel
from utils.security import (
    check_password,
    create_access_token,
    hash_password,
    validate_access_token,
)

user_router = APIRouter(prefix="/users", tags=["user"])
oauth2_scheme = OAuth2PasswordBearer("/users/login")


def validate_login(user_credentials: UserCredentials, db: Session = Depends(get_db)):
    user: User | None = storage.get_user_with_username(db, user_credentials.username)

    if user is not None and check_password(
        user_credentials.password, user.password_hash
    ):
        return user

    raise HTTPException(status_code=401, detail="Incorrect username or password")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    user_id: int = validate_access_token(token)
    user: User | None = storage.get_user_with_id(db, user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def validate_username_unique(username: str, db: Session):
    user: User | None = storage.get_user_with_username(db, username)
    if user is None:
        return
    raise HTTPException(status_code=409, detail="username already taken")


@user_router.post("/signup", status_code=201, response_model=UserModel)
def signup_user(
    user_credentials: UserCredentials, db: Session = Depends(get_db)
) -> User:
    validate_username_unique(user_credentials.username, db)

    create_dict = user_credentials.model_dump()
    create_dict["password_hash"] = hash_password(create_dict.pop("password"))
    return storage.post_user(db, create_dict)


@user_router.post("/login", response_model=AccessToken)
def login_user(user: User = Depends(validate_login)) -> User:
    return {"token": create_access_token(user.id)}


@user_router.get("/me", response_model=UserModel)
def get_user(user: User = Depends(get_current_user)):
    return user
