from pathlib import Path

import pytest

from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.learning.curriculum_mapping.models import (
    MappingStatus,
)
from backend.app.learning.curriculum_mapping.repository import (
    CurriculumMappingRepository,
)


MAP_PATH = Path(
    "examples/curriculum_mapping/"
    "kenya_grade9_integer_operations.json"
)


EXPECTED_CONCEPT_IDS = [
    "KE-G9-INTEGER-OPERATIONS",
    "KE-G9-INDICES-EXPONENTS",
    "ratio-and-proportion",
    "coordinate-graphs",
    "similarity",
    "trigonometry",
]


def build_repository() -> CurriculumMappingRepository:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    return CurriculumMappingRepository(
        curriculum_map
    )


def test_loads_six_concept_mappings() -> None:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    assert len(curriculum_map.mappings) == 6

    assert [
        mapping.concept_id
        for mapping in curriculum_map.mappings
    ] == EXPECTED_CONCEPT_IDS

    mapping = curriculum_map.mappings[0]

    assert (
        mapping.concept_id
        == "KE-G9-INTEGER-OPERATIONS"
    )

    assert (
        mapping.mapping_status
        == MappingStatus.REVIEW_REQUIRED
    )


def test_integer_concept_has_five_questions() -> None:
    repository = build_repository()

    questions = (
        repository.get_questions_for_concept(
            "KE-G9-INTEGER-OPERATIONS"
        )
    )

    assert len(questions) == 5


def test_questions_are_returned_in_sequence_order() -> None:
    repository = build_repository()

    questions = (
        repository.get_questions_for_concept(
            "KE-G9-INTEGER-OPERATIONS"
        )
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

    questions = (
        repository.get_questions_for_concept(
            "KE-G9-INTEGER-OPERATIONS"
        )
    )

    mastery_question = next(
        question
        for question in questions
        if question.question_id == "207630"
    )

    assert (
        mastery_question.required_for_mastery
        is True
    )

    assert (
        mastery_question.role.value
        == "mastery_check"
    )

    assert "mastery check" in (
        mastery_question.notes.lower()
    )


def test_question_resolves_to_concept() -> None:
    repository = build_repository()

    mapping = (
        repository.get_concept_for_question(
            "207591"
        )
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
        curriculum_map.mappings[0]
        .model_copy(
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


def test_integer_operations_links_to_indices() -> None:
    repository = build_repository()

    mapping = repository.get_mapping(
        "KE-G9-INTEGER-OPERATIONS"
    )

    assert mapping is not None

    assert mapping.next_concept_ids == [
        "KE-G9-INDICES-EXPONENTS"
    ]


def test_indices_concept_has_six_questions() -> None:
    repository = build_repository()

    questions = (
        repository.get_questions_for_concept(
            "KE-G9-INDICES-EXPONENTS"
        )
    )

    assert len(questions) == 6

    assert (
        questions[-1].question_id
        == "206946"
    )

    assert (
        questions[-1]
        .required_for_mastery
        is True
    )


def test_indices_links_to_ratio() -> None:
    repository = build_repository()

    mapping = repository.get_mapping(
        "KE-G9-INDICES-EXPONENTS"
    )

    assert mapping is not None

    assert mapping.next_concept_ids == [
        "ratio-and-proportion"
    ]


def test_ratio_concept_is_available() -> None:
    repository = build_repository()

    mapping = repository.get_mapping(
        "ratio-and-proportion"
    )

    assert mapping is not None

    assert (
        mapping.concept_name
        == "Ratio and Proportion"
    )

    questions = (
        repository.get_questions_for_concept(
            "ratio-and-proportion"
        )
    )

    assert len(questions) == 4

    assert (
        questions[-1].question_id
        == "207542"
    )

    assert (
        questions[-1]
        .required_for_mastery
        is True
    )


def test_all_26_questions_are_mapped() -> None:
    repository = build_repository()

    total = sum(
        len(
            repository.get_questions_for_concept(
                concept_id
            )
        )
        for concept_id
        in EXPECTED_CONCEPT_IDS
    )

    assert total == 26
