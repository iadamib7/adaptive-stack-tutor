from pydantic import BaseModel, Field

from backend.app.learning.session.models import (
    LearningSessionState,
)


class StartSessionRequest(BaseModel):
    student_id: int = Field(gt=0)
    concept_id: str = Field(min_length=1)


class SubmitSessionAnswerRequest(BaseModel):
    student_id: int = Field(gt=0)
    concept_id: str = Field(min_length=1)
    question_id: str = Field(min_length=1)

    student_answers: dict[str, str] = Field(
        min_length=1,
    )

    prt_name: str = Field(
        default="prt1",
        min_length=1,
    )

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    answer_note: str = Field(min_length=1)

    feedback: str | None = None
    penalty: float = Field(default=0.0, ge=0.0)
    seed: int | None = None


class SessionResponse(LearningSessionState):
    pass
