from pathlib import Path

import pytest

from backend.app.learning.concept_decision.engine import (
    ConceptDecisionEngine,
)
from backend.app.learning.concept_decision.models import (
    ConceptDecisionAction,
)
from backend.app.learning.concept_evidence.tracker import (
    ConceptEvidenceTracker,
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


def build_engine() -> tuple[
    ConceptDecisionEngine,
    ConceptEvidenceTracker,
]:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    mapping_repository = CurriculumMappingRepository(
        curriculum_map
    )

    tracker = ConceptEvidenceTracker(
        mapping_repository=mapping_repository
    )

    engine = ConceptDecisionEngine(
        mapping_repository=mapping_repository,
        evidence_tracker=tracker,
    )

    return engine, tracker


def record_correct(
    tracker: ConceptEvidenceTracker,
    question_id: str,
) -> None:
    tracker.record_outcome(
        student_id=1,
        question_id=question_id,
        outcome_code="prt1-1-T",
        score=1.0,
    )


def test_new_learner_starts_with_foundation() -> None:
    engine, _ = build_engine()

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.action == (
        ConceptDecisionAction.START_FOUNDATION
    )
    assert decision.next_question_id == "207582"
    assert "No evidence" in decision.reason


def test_after_addition_system_targets_subtraction() -> None:
    engine, tracker = build_engine()

    record_correct(tracker, "207582")

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.action == (
        ConceptDecisionAction.TARGET_PRACTICE
    )
    assert decision.next_question_id == "207596"


def test_failed_question_is_targeted_again() -> None:
    engine, tracker = build_engine()

    record_correct(tracker, "207582")

    tracker.record_outcome(
        student_id=1,
        question_id="207596",
        outcome_code="prt1-1-F",
        score=0.0,
    )

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.action == (
        ConceptDecisionAction.TARGET_PRACTICE
    )
    assert decision.next_question_id == "207596"
    assert "not yet demonstrated" in decision.reason


def test_partial_question_is_targeted_again() -> None:
    engine, tracker = build_engine()

    record_correct(tracker, "207582")

    tracker.record_outcome(
        student_id=1,
        question_id="207596",
        outcome_code="prt1-1-T",
        score=0.5,
    )

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.next_question_id == "207596"
    assert "partial evidence" in decision.reason


def test_regular_evidence_leads_to_mastery_check() -> None:
    engine, tracker = build_engine()

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
    ]:
        record_correct(tracker, question_id)

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.action == (
        ConceptDecisionAction.VERIFY_MASTERY
    )
    assert decision.next_question_id == "207630"
    assert "integrated mastery check" in decision.reason


def test_failed_mastery_check_is_repeated() -> None:
    engine, tracker = build_engine()

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
    ]:
        record_correct(tracker, question_id)

    tracker.record_outcome(
        student_id=1,
        question_id="207630",
        outcome_code="prt1-1-F",
        score=0.0,
    )

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.action == (
        ConceptDecisionAction.VERIFY_MASTERY
    )
    assert decision.next_question_id == "207630"


def test_mastered_concept_is_completed_without_next_link() -> None:
    engine, tracker = build_engine()

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
        "207630",
    ]:
        record_correct(tracker, question_id)

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.action == (
        ConceptDecisionAction.COMPLETE_CONCEPT
    )
    assert decision.concept_mastered is True
    assert decision.next_question_id is None
    assert decision.next_concept_id is None


def test_mastered_concept_advances_when_next_link_exists() -> None:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    curriculum_map.mappings[
        0
    ].next_concept_ids = [
        "KE-G10-ALGEBRA-ENTRY"
    ]

    mapping_repository = CurriculumMappingRepository(
        curriculum_map
    )

    tracker = ConceptEvidenceTracker(
        mapping_repository=mapping_repository
    )

    engine = ConceptDecisionEngine(
        mapping_repository=mapping_repository,
        evidence_tracker=tracker,
    )

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
        "207630",
    ]:
        tracker.record_outcome(
            student_id=1,
            question_id=question_id,
            outcome_code="prt1-1-T",
            score=1.0,
        )

    decision = engine.decide(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert decision.action == (
        ConceptDecisionAction.ADVANCE_CONCEPT
    )
    assert decision.next_concept_id == (
        "KE-G10-ALGEBRA-ENTRY"
    )


def test_unknown_concept_is_rejected() -> None:
    engine, _ = build_engine()

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        engine.decide(
            student_id=1,
            concept_id="UNKNOWN",
        )
