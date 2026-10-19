from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import HTTPException
from jose import JWTError, jwt

SECRET_KEY = "TESTING"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, password_hash: str):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: int) -> dict[str, str]:
    data = {"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(minutes=30)}
    return jwt.encode(data, SECRET_KEY, ALGORITHM)


def validate_access_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        print(payload)
        return int(payload.get("sub"))
    except JWTError, ValueError:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
