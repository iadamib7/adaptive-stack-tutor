from enum import Enum

from pydantic import BaseModel, Field


class MappingStatus(str, Enum):
    DEVELOPMENT = "development"
    REVIEW_REQUIRED = "review_required"
    VALIDATED = "validated"


class EvidenceRole(str, Enum):
    FOUNDATION = "foundation"
    PRACTICE = "practice"
    INTEGRATION = "integration"
    DIAGNOSTIC = "diagnostic"
    MASTERY_CHECK = "mastery_check"


class QuestionEvidence(BaseModel):
    question_id: str = Field(min_length=1)
    question_name: str = Field(min_length=1)

    source_profile_id: str = Field(min_length=1)
    source_file: str = Field(min_length=1)

    role: EvidenceRole
    sequence_order: int = Field(ge=1)

    required_for_mastery: bool = False
    notes: str | None = None


class ConceptQuestionMapping(BaseModel):
    concept_id: str = Field(min_length=1)
    concept_name: str = Field(min_length=1)

    curriculum_profile_id: str = Field(min_length=1)
    level_id: str = Field(min_length=1)

    strand: str = Field(min_length=1)
    sub_strand: str = Field(min_length=1)

    learning_outcome: str = Field(min_length=1)

    prerequisite_concept_ids: list[str] = Field(
        default_factory=list,
    )

    next_concept_ids: list[str] = Field(
        default_factory=list,
    )

    questions: list[QuestionEvidence] = Field(
        default_factory=list,
    )

    mapping_status: MappingStatus = (
        MappingStatus.REVIEW_REQUIRED
    )

    source_basis: str = Field(min_length=1)
    reviewer_notes: str | None = None


class CurriculumQuestionMap(BaseModel):
    version: str = Field(min_length=1)
    name: str = Field(min_length=1)

    intended_context: str = Field(min_length=1)
    development_context: str = Field(min_length=1)

    mappings: list[ConceptQuestionMapping] = Field(
        default_factory=list,
    )
