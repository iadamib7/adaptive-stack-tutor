from enum import Enum

from pydantic import BaseModel, Field


class CurriculumStage(str, Enum):
    JHS = "JHS"
    SHS = "SHS"


class QuestionMetadata(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    question_text: str = Field(min_length=1)

    topic: str = Field(min_length=1)
    concept: str = Field(min_length=1)
    sub_concept: str | None = None

    curriculum_stage: CurriculumStage
    difficulty: int = Field(ge=1, le=5)

    prerequisites: list[str] = Field(default_factory=list)
    learning_outcomes: list[str] = Field(default_factory=list)

    stack_identifier: str | None = None
    source: str = "mock"


class AssessmentOutcome(BaseModel):
    question_id: str = Field(min_length=1)
    correct: bool
    score: float = Field(ge=0.0, le=1.0)

    response_code: str | None = None
    misconception: str | None = None
    feedback: str | None = None

    attempt_number: int = Field(default=1, ge=1)
