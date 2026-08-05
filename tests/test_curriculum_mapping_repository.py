from pathlib import Path

import pytest

from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.learning.curriculum_mapping.models import (
    EvidenceRole,
    MappingStatus,
)
from backend.app.learning.curriculum_mapping.repository import (
    CurriculumMappingRepository,
)


MAP_PATH = Path(
    "examples/curriculum_mapping/"
    "kenya_grade9_integer_operations.json"
)


def build_repository() -> CurriculumMappingRepository:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    return CurriculumMappingRepository(
        curriculum_map
    )


def test_loads_integer_operations_mapping() -> None:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    assert len(curriculum_map.mappings) == 1

    mapping = curriculum_map.mappings[0]

    assert (
        mapping.concept_id
        == "KE-G9-INTEGER-OPERATIONS"
    )
    assert (
        mapping.mapping_status
        == MappingStatus.REVIEW_REQUIRED
    )


def test_concept_has_five_evidence_questions() -> None:
    repository = build_repository()

    questions = repository.get_questions_for_concept(
        "KE-G9-INTEGER-OPERATIONS"
    )

    assert len(questions) == 5


def test_questions_are_returned_in_sequence_order() -> None:
    repository = build_repository()

    questions = repository.get_questions_for_concept(
        "KE-G9-INTEGER-OPERATIONS"
    )

    assert [
        question.question_id
        for question in questions
    ] == [
        "207582",
        "207596",
        "207591",
        "207589",
        "207630",
    ]


def test_combined_operations_is_mastery_check() -> None:
    repository = build_repository()

    mastery_questions = (
        repository.get_mastery_questions(
            "KE-G9-INTEGER-OPERATIONS"
        )
    )

    assert len(mastery_questions) == 1
    assert mastery_questions[0].question_id == (
        "207630"
    )
    assert mastery_questions[0].role == (
        EvidenceRole.MASTERY_CHECK
    )


def test_question_resolves_to_concept() -> None:
    repository = build_repository()

    mapping = repository.get_concept_for_question(
        "207591"
    )

    assert mapping is not None
    assert (
        mapping.concept_id
        == "KE-G9-INTEGER-OPERATIONS"
    )


def test_unknown_question_has_no_concept() -> None:
    repository = build_repository()

    assert (
        repository.get_concept_for_question(
            "UNKNOWN"
        )
        is None
    )


def test_unknown_concept_has_no_questions() -> None:
    repository = build_repository()

    assert (
        repository.get_questions_for_concept(
            "UNKNOWN"
        )
        == []
    )


def test_duplicate_question_mapping_is_rejected() -> None:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    duplicate_mapping = (
        curriculum_map.mappings[0].model_copy(
            deep=True
        )
    )

    duplicate_mapping.concept_id = (
        "KE-G9-DUPLICATE"
    )

    curriculum_map.mappings.append(
        duplicate_mapping
    )

    with pytest.raises(
        ValueError,
        match="mapped to more than one concept",
    ):
        CurriculumMappingRepository(
            curriculum_map
        )
