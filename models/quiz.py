from pydantic import BaseModel, Field, model_validator


class QuizPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    author: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        fields = ("name",)
        for field in fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class QuizCreate(BaseModel):
    name: str = Field(min_length=1)
    author: str | None = Field(default=None, min_length=1)


class QuizModel(QuizCreate):
    id: int = Field(ge=0)
