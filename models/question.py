from pydantic import BaseModel, Field, model_validator


class QuestionPatch(BaseModel):
    question: str | None = Field(default=None, min_length=1)
    options: list[str] | None = None
    answer_index: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        fields = ("question", "options", "answer_index")
        for field in fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class QuestionCreate(BaseModel):
    question: str = Field(min_length=1)
    options: list[str]
    answer_index: int = Field(ge=0)


class QuestionModel(BaseModel):
    id: int = Field(ge=0)
    quiz_id: int = Field(ge=0)
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=2)
