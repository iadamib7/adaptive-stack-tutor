from pydantic import BaseModel, Field

from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
)


class SessionQuestion(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class SessionProgress(BaseModel):
    concept_id: str = Field(min_length=1)
    concept_name: str = Field(min_length=1)

    attempts: int = Field(ge=0)
    evidence_score: float = Field(ge=0.0, le=1.0)

    positive_evidence_count: int = Field(ge=0)
    partial_evidence_count: int = Field(ge=0)
    negative_evidence_count: int = Field(ge=0)

    concept_mastered: bool


class LearningSessionState(BaseModel):
    student_id: int = Field(gt=0)
    current_concept_id: str = Field(min_length=1)

    question: SessionQuestion | None

    action: ConceptDecisionAction
    feedback: str = Field(min_length=1)
    decision_reason: str = Field(min_length=1)

    progress: SessionProgress

    next_concept_id: str | None = None
    session_complete: bool = False


class ScoredStackOutcome(BaseModel):
    student_id: int = Field(gt=0)

    concept_id: str = Field(min_length=1)
    question_id: str = Field(min_length=1)

    outcome_code: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)

    stack_feedback: str | None = None
