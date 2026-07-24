from enum import Enum

from pydantic import BaseModel, Field


class DifficultyLevel(int, Enum):
    BEGINNER = 1
    EASY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class Question(BaseModel):
    id: int = Field(gt=0)
    course: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    concept: str = Field(min_length=1)
    difficulty: DifficultyLevel
    question_text: str = Field(min_length=1)
    correct_answer: str = Field(min_length=1)
    prerequisite: str | None = None
    learning_outcome: str = Field(min_length=1)
    common_errors: list[str] = Field(default_factory=list)
    remediation_concept: str | None = None
    stack_identifier: str | None = None