from pydantic import BaseModel, Field


class Student(BaseModel):
    id: int
    name: str

    attempts: int = 0
    correct: int = 0
    incorrect: int = 0

    mastery: dict[str, float] = Field(default_factory=dict)


       