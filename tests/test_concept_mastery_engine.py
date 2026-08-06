from pathlib import Path

import pytest

from backend.app.learning.concept_evidence.tracker import (
    ConceptEvidenceTracker,
)
from backend.app.learning.concept_mastery.engine import (
    ConceptMasteryEngine,
)
from backend.app.learning.concept_mastery.models import (
    MasteryStatus,
)
from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.learning.curriculum_mapping.repository import (
    CurriculumMappingRepository,
)


MAP_PATH = Path(
    "examples/curriculum_mapping/"
    "kenya_grade9_integer_operations.json"
)

CONCEPT_ID = "KE-G9-INTEGER-OPERATIONS"


def build_components() -> tuple[
    ConceptMasteryEngine,
    ConceptEvidenceTracker,
]:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    mapping_repository = CurriculumMappingRepository(
        curriculum_map
    )

    evidence_tracker = ConceptEvidenceTracker(
        mapping_repository=mapping_repository
    )

    mastery_engine = ConceptMasteryEngine(
        mapping_repository=mapping_repository,
        evidence_tracker=evidence_tracker,
    )

    return mastery_engine, evidence_tracker


def record(
    tracker: ConceptEvidenceTracker,
    question_id: str,
    score: float,
) -> None:
    tracker.record_outcome(
        student_id=1,
        question_id=question_id,
        outcome_code=(
            "prt1-1-T"
            if score > 0.0
            else "prt1-1-F"
        ),
        score=score,
    )


def test_new_concept_is_not_started() -> None:
    engine, _ = build_components()

    state = engine.evaluate(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert state.status == MasteryStatus.NOT_STARTED
    assert state.mastery_score == 0.0
    assert state.confidence == 0.0


def test_first_attempt_introduces_concept() -> None:
    engine, tracker = build_components()

    record(tracker, "207582", 1.0)

    state = engine.evaluate(1, CONCEPT_ID)

    assert state.status == MasteryStatus.INTRODUCED
    assert state.attempts == 1


def test_two_attempts_move_to_learning() -> None:
    engine, tracker = build_components()

    record(tracker, "207582", 1.0)
    record(tracker, "207596", 1.0)

    state = engine.evaluate(1, CONCEPT_ID)

    assert state.status == MasteryStatus.LEARNING


def test_three_attempts_move_to_practicing() -> None:
    engine, tracker = build_components()

    record(tracker, "207582", 1.0)
    record(tracker, "207596", 1.0)
    record(tracker, "207591", 0.0)

    state = engine.evaluate(1, CONCEPT_ID)

    assert state.status == MasteryStatus.PRACTICING
    assert state.negative_evidence_count == 1


def test_partial_evidence_is_preserved() -> None:
    engine, tracker = build_components()

    record(tracker, "207582", 0.5)

    state = engine.evaluate(1, CONCEPT_ID)

    assert state.partial_evidence_count == 1
    assert state.mastery_score == 0.5


def test_full_success_results_in_mastery() -> None:
    engine, tracker = build_components()

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
        "207630",
    ]:
        record(tracker, question_id, 1.0)

    state = engine.evaluate(1, CONCEPT_ID)

    assert state.status == MasteryStatus.MASTERED
    assert state.mastery_score == 1.0
    assert state.passed_mastery_checks == 1
    assert state.confidence >= 0.8


def test_failure_after_mastery_requires_review() -> None:
    engine, tracker = build_components()

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
        "207630",
    ]:
        record(tracker, question_id, 1.0)

    mastered_state = engine.evaluate(
        1,
        CONCEPT_ID,
    )

    assert (
        mastered_state.status
        == MasteryStatus.MASTERED
    )

    record(tracker, "207630", 0.0)

    review_state = engine.evaluate(
        1,
        CONCEPT_ID,
    )

    assert (
        review_state.status
        == MasteryStatus.REVIEW_REQUIRED
    )


def test_confidence_increases_with_more_evidence() -> None:
    engine, tracker = build_components()

    record(tracker, "207582", 1.0)

    first_state = engine.evaluate(
        1,
        CONCEPT_ID,
    )

    record(tracker, "207596", 1.0)
    record(tracker, "207591", 1.0)

    later_state = engine.evaluate(
        1,
        CONCEPT_ID,
    )

    assert (
        later_state.confidence
        > first_state.confidence
    )


def test_mastery_state_is_saved() -> None:
    engine, tracker = build_components()

    record(tracker, "207582", 1.0)

    evaluated_state = engine.evaluate(
        1,
        CONCEPT_ID,
    )

    stored_state = engine.get_state(
        1,
        CONCEPT_ID,
    )

    assert stored_state == evaluated_state


def test_unknown_concept_is_rejected() -> None:
    engine, _ = build_components()

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        engine.evaluate(
            student_id=1,
            concept_id="UNKNOWN",
        )
