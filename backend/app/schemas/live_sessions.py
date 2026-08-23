from typing import Any

from pydantic import BaseModel, Field

from backend.app.learning.session.models import (
    LearningSessionState,
)


class StartLiveSessionRequest(BaseModel):
    student_id: int = Field(gt=0)

    curriculum_profile_id: str | None = Field(
        default=None,
        min_length=1,
    )

    concept_id: str | None = Field(
        default=None,
        min_length=1,
    )


class SubmitLiveAnswerRequest(BaseModel):
    student_id: int = Field(gt=0)
    concept_id: str = Field(min_length=1)
    question_id: str = Field(min_length=1)

    student_answers: dict[str, str] = Field(
        min_length=1,
    )

    seed: int = Field(gt=0)

    target_prt_name: str | None = None

    target_prt_names: list[str] = Field(
        default_factory=list,
    )


class RenderedStackQuestion(BaseModel):
    question_id: str
    seed: int
    html: str
    inputs: dict[str, Any]

    task_id: str | None = None

    task_input_names: list[str] = Field(
        default_factory=list,
    )

    task_prt_names: list[str] = Field(
        default_factory=list,
    )

    task_index: int = Field(
        default=0,
        ge=0,
    )

    task_count: int = Field(
        default=1,
        ge=1,
    )

    worked_solution: str
    question_note: str
    available_variants: list[int]



class LiveSessionResponse(BaseModel):
    session: LearningSessionState

    rendered_question: (
        RenderedStackQuestion | None
    )

    submitted_feedback: str | None = None

    preparation_message: str | None = None
