from datetime import UTC, datetime, timedelta
from os import getenv

import bcrypt
from dotenv import load_dotenv
from fastapi import HTTPException
from jose import JWTError, jwt

load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = "HS256"

if SECRET_KEY is None:
    raise ValueError(".env does not contain SECRET_KEY")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, password_hash: str):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: int) -> dict[str, str]:
    data = {"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(days=3)}
    return jwt.encode(data, SECRET_KEY, ALGORITHM)


def validate_access_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        return int(payload.get("sub"))
    except JWTError, ValueError:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
