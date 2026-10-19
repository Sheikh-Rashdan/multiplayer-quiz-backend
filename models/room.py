from datetime import datetime

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    quiz_id: int = Field(ge=1)


class RoomModel(BaseModel):
    id: str = Field(min_length=5, max_length=5)
    host_id: int = Field(ge=1)
    quiz_id: int = Field(ge=1)
    status: str = Field(default="waiting", min_length=1)
    player_ids: list[int] = Field(default_factory=list)
    question_index: int = Field(default=0, ge=0)
    created_at: datetime
