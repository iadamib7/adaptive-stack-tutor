from enum import Enum

from pydantic import BaseModel, Field


class ConceptStatus(str, Enum):
    FOUNDATION = "foundation"
    TRANSITION = "transition"
    TARGET = "target"


class CurriculumIdentity(BaseModel):
    """
    Identifies one curriculum profile without embedding a specific
    country or school system into the adaptive engine.
    """

    id: str = Field(min_length=1)
    country: str = Field(min_length=1)
    education_system: str = Field(min_length=1)

    source_level_id: str = Field(min_length=1)
    source_level_label: str = Field(min_length=1)

    target_level_id: str = Field(min_length=1)
    target_level_label: str = Field(min_length=1)

    curriculum_version: str = Field(min_length=1)


class CurriculumConcept(BaseModel):
    id: str = Field(min_length=1)

    level_id: str = Field(min_length=1)
    level_label: str = Field(min_length=1)
    progression_order: int = Field(ge=0)

    strand: str = Field(min_length=1)
    sub_strand: str = Field(min_length=1)

    name: str = Field(min_length=1)
    description: str | None = None

    learning_outcomes: list[str] = Field(
        default_factory=list,
    )

    prerequisite_concept_ids: list[str] = Field(
        default_factory=list,
    )

    next_concept_ids: list[str] = Field(
        default_factory=list,
    )

    stack_question_ids: list[str] = Field(
        default_factory=list,
    )

    status: ConceptStatus = ConceptStatus.FOUNDATION


class CurriculumMap(BaseModel):
    version: str = Field(min_length=1)
    name: str = Field(min_length=1)

    identity: CurriculumIdentity

    intended_use: str = Field(min_length=1)
    development_status: str = Field(min_length=1)

    source_documents: list[str] = Field(
        default_factory=list,
    )

    concepts: list[CurriculumConcept] = Field(
        default_factory=list,
    )
