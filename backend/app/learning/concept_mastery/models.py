from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MasteryStatus(str, Enum):
    NOT_STARTED = "not_started"
    INTRODUCED = "introduced"
    LEARNING = "learning"
    PRACTICING = "practicing"
    MASTERED = "mastered"
    REVIEW_REQUIRED = "review_required"


class ConceptMasteryState(BaseModel):
    student_id: int = Field(gt=0)

    concept_id: str = Field(min_length=1)
    concept_name: str = Field(min_length=1)

    mastery_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    attempts: int = Field(ge=0)

    positive_evidence_count: int = Field(ge=0)
    partial_evidence_count: int = Field(ge=0)
    negative_evidence_count: int = Field(ge=0)

    required_mastery_checks: int = Field(ge=0)
    passed_mastery_checks: int = Field(ge=0)

    status: MasteryStatus
    explanation: str = Field(min_length=1)

    last_updated: datetime
