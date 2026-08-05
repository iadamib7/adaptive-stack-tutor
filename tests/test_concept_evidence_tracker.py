from pathlib import Path

import pytest

from backend.app.learning.concept_evidence.models import (
    EvidenceType,
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


def build_tracker() -> ConceptEvidenceTracker:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    mapping_repository = CurriculumMappingRepository(
        curriculum_map
    )

    return ConceptEvidenceTracker(
        mapping_repository=mapping_repository
    )


def test_correct_outcome_creates_positive_evidence() -> None:
    tracker = build_tracker()

    event = tracker.record_outcome(
        student_id=1,
        question_id="207582",
        outcome_code="prt1-1-T",
        score=1.0,
    )

    assert event.concept_id == CONCEPT_ID
    assert event.evidence_type == EvidenceType.POSITIVE
    assert event.evidence_weight == 1.0


def test_partial_score_creates_partial_evidence() -> None:
    tracker = build_tracker()

    event = tracker.record_outcome(
        student_id=1,
        question_id="207582",
        outcome_code="prt1-1-T",
        score=0.5,
    )

    assert event.evidence_type == EvidenceType.PARTIAL


def test_incorrect_outcome_creates_negative_evidence() -> None:
    tracker = build_tracker()

    event = tracker.record_outcome(
        student_id=1,
        question_id="207596",
        outcome_code="prt1-1-F",
        score=0.0,
    )

    assert event.evidence_type == EvidenceType.NEGATIVE
    assert "still needs support" in event.explanation


def test_mastery_question_has_extra_weight() -> None:
    tracker = build_tracker()

    event = tracker.record_outcome(
        student_id=1,
        question_id="207630",
        outcome_code="prt1-1-T",
        score=1.0,
    )

    assert event.required_for_mastery is True
    assert event.evidence_weight == 2.0


def test_unmapped_question_is_rejected() -> None:
    tracker = build_tracker()

    with pytest.raises(
        ValueError,
        match="not mapped to a curriculum concept",
    ):
        tracker.record_outcome(
            student_id=1,
            question_id="UNKNOWN",
            outcome_code="prt1-1-T",
            score=1.0,
        )


def test_summary_counts_evidence_types() -> None:
    tracker = build_tracker()

    tracker.record_outcome(
        1,
        "207582",
        "prt1-1-T",
        1.0,
    )

    tracker.record_outcome(
        1,
        "207596",
        "prt1-1-F",
        0.0,
    )

    tracker.record_outcome(
        1,
        "207591",
        "prt1-1-T",
        0.5,
    )

    summary = tracker.summarize(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert summary.attempts == 3
    assert summary.positive_evidence_count == 1
    assert summary.partial_evidence_count == 1
    assert summary.negative_evidence_count == 1
    assert summary.concept_mastered is False


def test_mastery_requires_mastery_check() -> None:
    tracker = build_tracker()

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
    ]:
        tracker.record_outcome(
            student_id=1,
            question_id=question_id,
            outcome_code="prt1-1-T",
            score=1.0,
        )

    summary = tracker.summarize(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert summary.evidence_score == 1.0
    assert summary.concept_mastered is False
    assert "mastery-check" in summary.recommendation


def test_mastery_check_and_sufficient_evidence_master_concept() -> None:
    tracker = build_tracker()

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

    summary = tracker.summarize(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert summary.evidence_score == 1.0
    assert summary.concept_mastered is True
    assert summary.passed_mastery_question_ids == [
        "207630"
    ]
    assert "next curriculum concept" in (
        summary.recommendation
    )


def test_failed_mastery_check_prevents_mastery() -> None:
    tracker = build_tracker()

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
    ]:
        tracker.record_outcome(
            student_id=1,
            question_id=question_id,
            outcome_code="prt1-1-T",
            score=1.0,
        )

    tracker.record_outcome(
        student_id=1,
        question_id="207630",
        outcome_code="prt1-1-F",
        score=0.0,
    )

    summary = tracker.summarize(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert summary.concept_mastered is False
    assert summary.passed_mastery_question_ids == []
