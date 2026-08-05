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
from backend.app.learning.session.engine import (
    AdaptiveLearningSessionEngine,
)
from backend.app.learning.session.models import (
    ScoredStackOutcome,
)


MAP_PATH = Path(
    "examples/curriculum_mapping/"
    "kenya_grade9_integer_operations.json"
)

CONCEPT_ID = "KE-G9-INTEGER-OPERATIONS"


def build_session_engine() -> (
    AdaptiveLearningSessionEngine
):
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    mapping_repository = CurriculumMappingRepository(
        curriculum_map
    )

    tracker = ConceptEvidenceTracker(
        mapping_repository=mapping_repository
    )

    decision_engine = ConceptDecisionEngine(
        mapping_repository=mapping_repository,
        evidence_tracker=tracker,
    )

    return AdaptiveLearningSessionEngine(
        evidence_tracker=tracker,
        decision_engine=decision_engine,
    )


def submit_correct(
    engine: AdaptiveLearningSessionEngine,
    student_id: int,
    concept_id: str,
    question_id: str,
) -> None:
    engine.submit_outcome(
        ScoredStackOutcome(
            student_id=student_id,
            concept_id=concept_id,
            question_id=question_id,
            outcome_code="prt1-1-T",
            score=1.0,
            stack_feedback="Correct answer, well done.",
        )
    )


def test_new_session_starts_with_foundation_question() -> None:
    engine = build_session_engine()

    session = engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert session.action == (
        ConceptDecisionAction.START_FOUNDATION
    )
    assert session.question is not None
    assert session.question.id == "207582"
    assert session.progress.attempts == 0
    assert session.session_complete is False


def test_correct_answer_moves_to_next_question() -> None:
    engine = build_session_engine()

    engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    session = engine.submit_outcome(
        ScoredStackOutcome(
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id="207582",
            outcome_code="prt1-1-T",
            score=1.0,
            stack_feedback="Correct answer, well done.",
        )
    )

    assert session.action == (
        ConceptDecisionAction.TARGET_PRACTICE
    )
    assert session.question is not None
    assert session.question.id == "207596"
    assert session.progress.attempts == 1
    assert session.progress.positive_evidence_count == 1
    assert "Correct answer" in session.feedback


def test_incorrect_answer_repeats_targeted_skill() -> None:
    engine = build_session_engine()

    engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    session = engine.submit_outcome(
        ScoredStackOutcome(
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id="207582",
            outcome_code="prt1-1-F",
            score=0.0,
            stack_feedback=(
                "Review how integer addition works."
            ),
        )
    )

    assert session.action == (
        ConceptDecisionAction.TARGET_PRACTICE
    )
    assert session.question is not None
    assert session.question.id == "207582"
    assert session.progress.negative_evidence_count == 1
    assert "Review" in session.feedback


def test_partial_answer_creates_partial_progress() -> None:
    engine = build_session_engine()

    engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    session = engine.submit_outcome(
        ScoredStackOutcome(
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id="207582",
            outcome_code="prt1-1-T",
            score=0.5,
        )
    )

    assert session.progress.partial_evidence_count == 1
    assert session.progress.evidence_score == 0.5
    assert session.question is not None
    assert session.question.id == "207582"


def test_regular_questions_lead_to_mastery_check() -> None:
    engine = build_session_engine()

    session = engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    assert session.question is not None

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
    ]:
        assert session.question is not None
        assert session.question.id == question_id

        submit_correct(
            engine=engine,
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id=question_id,
        )

        session = engine.get_session(1)
        assert session is not None

    assert session.action == (
        ConceptDecisionAction.VERIFY_MASTERY
    )
    assert session.question is not None
    assert session.question.id == "207630"


def test_passing_mastery_check_completes_concept() -> None:
    engine = build_session_engine()

    session = engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    for question_id in [
        "207582",
        "207596",
        "207591",
        "207589",
        "207630",
    ]:
        assert session.question is not None
        assert session.question.id == question_id

        submit_correct(
            engine=engine,
            student_id=1,
            concept_id=CONCEPT_ID,
            question_id=question_id,
        )

        session = engine.get_session(1)
        assert session is not None

    assert session.action == (
        ConceptDecisionAction.COMPLETE_CONCEPT
    )
    assert session.progress.concept_mastered is True
    assert session.question is None
    assert session.session_complete is True


def test_submission_requires_active_session() -> None:
    engine = build_session_engine()

    with pytest.raises(
        ValueError,
        match="No active learning session",
    ):
        engine.submit_outcome(
            ScoredStackOutcome(
                student_id=1,
                concept_id=CONCEPT_ID,
                question_id="207582",
                outcome_code="prt1-1-T",
                score=1.0,
            )
        )


def test_wrong_question_submission_is_rejected() -> None:
    engine = build_session_engine()

    engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        engine.submit_outcome(
            ScoredStackOutcome(
                student_id=1,
                concept_id=CONCEPT_ID,
                question_id="207596",
                outcome_code="prt1-1-T",
                score=1.0,
            )
        )


def test_wrong_concept_submission_is_rejected() -> None:
    engine = build_session_engine()

    engine.start_session(
        student_id=1,
        concept_id=CONCEPT_ID,
    )

    with pytest.raises(
        ValueError,
        match="concept does not match",
    ):
        engine.submit_outcome(
            ScoredStackOutcome(
                student_id=1,
                concept_id="WRONG-CONCEPT",
                question_id="207582",
                outcome_code="prt1-1-T",
                score=1.0,
            )
        )
