from pathlib import Path

from backend.app.learning.curriculum_mapping.builder import (
    build_default_curriculum,
    write_curriculum,
)
from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)


EXPECTED_CONCEPT_IDS = [
    "KE-G9-INTEGER-OPERATIONS",
    "KE-G9-INDICES-EXPONENTS",
    "ratio-and-proportion",
    "coordinate-graphs",
    "similarity",
    "trigonometry",
]


def test_builder_creates_six_concepts() -> None:
    curriculum = build_default_curriculum()

    assert len(curriculum["mappings"]) == 6

    concept_ids = [
        mapping["concept_id"]
        for mapping in curriculum["mappings"]
    ]

    assert concept_ids == EXPECTED_CONCEPT_IDS


def test_integer_operations_links_to_indices() -> None:
    curriculum = build_default_curriculum()

    integer_mapping = curriculum["mappings"][0]

    assert integer_mapping[
        "next_concept_ids"
    ] == [
        "KE-G9-INDICES-EXPONENTS"
    ]


def test_integer_mastery_question_is_flagged() -> None:
    curriculum = build_default_curriculum()

    integer_mapping = curriculum["mappings"][0]

    mastery_question = next(
        question
        for question in integer_mapping["questions"]
        if question["required_for_mastery"]
    )

    assert (
        mastery_question["question_id"]
        == "207630"
    )

    assert (
        mastery_question["role"]
        == "mastery_check"
    )

    assert "mastery check" in (
        mastery_question["notes"].lower()
    )


def test_indices_has_six_questions() -> None:
    curriculum = build_default_curriculum()

    indices_mapping = curriculum["mappings"][1]

    assert len(
        indices_mapping["questions"]
    ) == 6

    assert (
        indices_mapping["questions"][-1]
        ["required_for_mastery"]
        is True
    )


def test_builder_contains_26_questions() -> None:
    curriculum = build_default_curriculum()

    question_count = sum(
        len(mapping["questions"])
        for mapping in curriculum["mappings"]
    )

    assert question_count == 26


def test_written_curriculum_loads(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path / "curriculum.json"
    )

    write_curriculum(output_path)

    loaded = load_curriculum_question_map(
        output_path
    )

    assert len(loaded.mappings) == 6

    assert [
        mapping.concept_id
        for mapping in loaded.mappings
    ] == EXPECTED_CONCEPT_IDS

    assert (
        loaded.mappings[0]
        .next_concept_ids
        == [
            "KE-G9-INDICES-EXPONENTS"
        ]
    )
