from enum import Enum

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    POSITIVE = "positive"
    PARTIAL = "partial"
    NEGATIVE = "negative"


class ConceptEvidenceEvent(BaseModel):
    student_id: int = Field(gt=0)

    concept_id: str = Field(min_length=1)
    question_id: str = Field(min_length=1)
    question_name: str = Field(min_length=1)

    outcome_code: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)

    evidence_type: EvidenceType
    evidence_weight: float = Field(gt=0.0)

    required_for_mastery: bool = False
    explanation: str = Field(min_length=1)


class ConceptEvidenceSummary(BaseModel):
    student_id: int = Field(gt=0)
    concept_id: str = Field(min_length=1)
    concept_name: str = Field(min_length=1)

    attempts: int = Field(ge=0)

    positive_evidence_count: int = Field(ge=0)
    partial_evidence_count: int = Field(ge=0)
    negative_evidence_count: int = Field(ge=0)

    earned_weight: float = Field(ge=0.0)
    possible_weight: float = Field(ge=0.0)

    evidence_score: float = Field(ge=0.0, le=1.0)

    required_mastery_question_ids: list[str] = Field(
        default_factory=list,
    )

    passed_mastery_question_ids: list[str] = Field(
        default_factory=list,
    )

    concept_mastered: bool = False
    recommendation: str = Field(min_length=1)
