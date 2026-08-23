from enum import Enum

from pydantic import BaseModel, Field


class ConceptStatus(str, Enum):
    FOUNDATION = "foundation"
    TRANSITION = "transition"
    TARGET = "target"


class CurriculumIdentity(BaseModel):
    """
    Identifies one curriculum profile without embedding a
    specific country or school system into the adaptive
    engine.
    """

    id: str = Field(min_length=1)

    country: str = Field(min_length=1)

    education_system: str = Field(
        min_length=1,
    )

    source_level_id: str = Field(
        min_length=1,
    )

    source_level_label: str = Field(
        min_length=1,
    )

    target_level_id: str = Field(
        min_length=1,
    )

    target_level_label: str = Field(
        min_length=1,
    )

    curriculum_version: str = Field(
        min_length=1,
    )


class CurriculumConcept(BaseModel):
    """
    A concept as it appears in one curriculum.

    knowledge_concept_id identifies the primary shared
    mathematical concept.

    supporting_knowledge_concept_ids identifies other
    shared concepts required or assessed by the same
    curriculum concept.
    """

    id: str = Field(min_length=1)

    knowledge_concept_id: str | None = None

    supporting_knowledge_concept_ids: list[str] = Field(
        default_factory=list,
    )

    level_id: str = Field(min_length=1)

    level_label: str = Field(min_length=1)

    progression_order: int = Field(ge=0)

    strand: str = Field(min_length=1)

    sub_strand: str = Field(min_length=1)

    name: str = Field(min_length=1)

    description: str | None = None

    content_standard_ids: list[str] = Field(
        default_factory=list,
    )

    learning_indicator_ids: list[str] = Field(
        default_factory=list,
    )

    learning_outcomes: list[str] = Field(
        default_factory=list,
    )

    readiness_target_ids: list[str] = Field(
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

    status: ConceptStatus = (
        ConceptStatus.FOUNDATION
    )


class CurriculumMap(BaseModel):
    version: str = Field(min_length=1)

    name: str = Field(min_length=1)

    identity: CurriculumIdentity

    intended_use: str = Field(
        min_length=1,
    )

    development_status: str = Field(
        min_length=1,
    )

    source_documents: list[str] = Field(
        default_factory=list,
    )

    concepts: list[CurriculumConcept] = Field(
        default_factory=list,
    )
