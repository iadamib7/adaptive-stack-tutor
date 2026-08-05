from enum import Enum

from pydantic import BaseModel, Field


class ConceptDecisionAction(str, Enum):
    START_FOUNDATION = "start_foundation"
    TARGET_PRACTICE = "target_practice"
    VERIFY_MASTERY = "verify_mastery"
    ADVANCE_CONCEPT = "advance_concept"
    COMPLETE_CONCEPT = "complete_concept"


class ConceptLearningDecision(BaseModel):
    student_id: int = Field(gt=0)

    current_concept_id: str = Field(min_length=1)
    current_concept_name: str = Field(min_length=1)

    action: ConceptDecisionAction

    next_question_id: str | None = None
    next_question_name: str | None = None
    next_concept_id: str | None = None

    evidence_score: float = Field(ge=0.0, le=1.0)
    concept_mastered: bool

    reason: str = Field(min_length=1)
