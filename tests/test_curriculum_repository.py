from pathlib import Path

from backend.app.learning.curriculum.loader import (
    load_curriculum_map,
)
from backend.app.learning.curriculum.models import (
    ConceptStatus,
)
from backend.app.learning.curriculum.repository import (
    CurriculumRepository,
)


MAP_PATH = Path(
    "examples/curriculum/transition_map.json"
)


def build_repository() -> CurriculumRepository:
    curriculum_map = load_curriculum_map(MAP_PATH)
    return CurriculumRepository(curriculum_map)


def test_loads_curriculum_identity() -> None:
    curriculum_map = load_curriculum_map(MAP_PATH)

    assert curriculum_map.version == "0.2"
    assert curriculum_map.identity.country == "Kenya"
    assert curriculum_map.identity.source_level_id == "KE-G9"
    assert curriculum_map.identity.target_level_id == "KE-G10"


def test_profile_documents_intended_ghanaian_use() -> None:
    curriculum_map = load_curriculum_map(MAP_PATH)

    assert "Ghanaian" in curriculum_map.intended_use
    assert "Development" in (
        curriculum_map.identity.curriculum_version
    )


def test_get_concept_by_id() -> None:
    repository = build_repository()

    concept = repository.get_concept(
        "KE-G9-ALG-FOUNDATION"
    )

    assert concept is not None
    assert concept.level_id == "KE-G9"
    assert concept.status == ConceptStatus.FOUNDATION


def test_get_grade_9_concepts() -> None:
    repository = build_repository()

    concepts = repository.get_concepts_by_level(
        "KE-G9"
    )

    assert len(concepts) == 2


def test_level_lookup_is_case_insensitive() -> None:
    repository = build_repository()

    concepts = repository.get_concepts_by_level(
        "ke-g10"
    )

    assert len(concepts) == 1
    assert concepts[0].id == "KE-G10-ALG-ENTRY"


def test_get_prerequisite_concept() -> None:
    repository = build_repository()

    prerequisites = repository.get_prerequisites(
        "KE-G10-ALG-ENTRY"
    )

    assert len(prerequisites) == 1
    assert prerequisites[0].id == (
        "KE-G9-ALG-TRANSITION"
    )


def test_get_next_concept() -> None:
    repository = build_repository()

    next_concepts = repository.get_next_concepts(
        "KE-G9-ALG-TRANSITION"
    )

    assert len(next_concepts) == 1
    assert next_concepts[0].id == (
        "KE-G10-ALG-ENTRY"
    )


def test_get_ordered_transition_pathway() -> None:
    repository = build_repository()

    pathway = repository.get_ordered_pathway()

    assert [
        concept.id
        for concept in pathway
    ] == [
        "KE-G9-ALG-FOUNDATION",
        "KE-G9-ALG-TRANSITION",
        "KE-G10-ALG-ENTRY",
    ]


def test_unknown_concept_returns_none() -> None:
    repository = build_repository()

    assert repository.get_concept("UNKNOWN") is None


def test_unknown_concept_has_no_questions() -> None:
    repository = build_repository()

    assert (
        repository.get_questions_for_concept(
            "UNKNOWN"
        )
        == []
    )
