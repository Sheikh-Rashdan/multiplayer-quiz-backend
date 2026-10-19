from pydantic import BaseModel, Field


class UserCredentials(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserModel(BaseModel):
    id: int = Field(ge=1)
    username: str = Field(min_length=1)


class AccessToken(BaseModel):
    token: str
