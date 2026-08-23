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

GHANA_MAP_PATH = Path(
    "examples/curriculum_mapping/"
    "ghana_basic9_linear_readiness.json"
)

GHANA_CONCEPT_ID = "simultaneous-equations"


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



def build_ghana_session_engine() -> (
    AdaptiveLearningSessionEngine
):
    curriculum_map = load_curriculum_question_map(
        GHANA_MAP_PATH
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

    submit_correct(
        engine=engine,
        student_id=1,
        concept_id=CONCEPT_ID,
        question_id="207630",
    )

    session = engine.get_session(1)

    assert session is not None

    assert session.action == (
        ConceptDecisionAction.ADVANCE_CONCEPT
    )

    assert session.next_concept_id == (
        "KE-G9-INDICES-EXPONENTS"
    )



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



def test_first_attempt_uses_configured_adaptive_pathway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = build_session_engine()

    student_id = 90001

    # Obtain one valid ConceptLearningDecision object
    # before blocking the legacy decision engine.
    expected_decision = (
        engine.decision_engine.decide(
            student_id=student_id,
            concept_id=CONCEPT_ID,
        )
    )

    calls = {
        "policy": 0,
        "adapter": 0,
    }

    class FakePathwayPolicy:
        def decide(
            self,
            current_concept_id,
            mastered_concept_ids,
            seen_content_ids=None,
            *,
            concept_mastered,
            repeat_attempt_counts=None,
        ):
            calls["policy"] += 1

            assert (
                current_concept_id
                == CONCEPT_ID
            )

            assert concept_mastered is False

            assert seen_content_ids == set()

            assert isinstance(
                mastered_concept_ids,
                set,
            )

            return object()

    class FakePathwayAdapter:
        def adapt(
            self,
            *,
            student_id,
            current_concept_id,
            pathway_decision,
            evidence_score,
            concept_mastered,
        ):
            calls["adapter"] += 1

            assert student_id == 90001

            assert (
                current_concept_id
                == CONCEPT_ID
            )

            assert pathway_decision is not None

            assert concept_mastered is False

            return expected_decision

    engine.pathway_policy = (
        FakePathwayPolicy()
    )

    engine.pathway_adapter = (
        FakePathwayAdapter()
    )

    def fail_if_legacy_used(
        *,
        student_id,
        concept_id,
    ):
        raise AssertionError(
            "Legacy decision engine must not "
            "handle the first attempt when an "
            "adaptive pathway is configured."
        )

    monkeypatch.setattr(
        engine.decision_engine,
        "decide",
        fail_if_legacy_used,
    )

    session = engine.start_session(
        student_id=student_id,
        concept_id=CONCEPT_ID,
    )

    assert session.progress.attempts == 0

    assert calls["policy"] == 1
    assert calls["adapter"] == 1

    assert session.question is not None


def test_ghana_qlin12_is_required_before_simultaneous_equations_mastery(
) -> None:
    engine = build_ghana_session_engine()

    student_id = 92012

    expected_regular_questions = [
        "lr_01_table_linear_relation",
        "qlin_02_partial_table_linear_relation",
        "qlin_03_paired_linear_tables",
        "qlin_04_distinct_representation_tables",
        "qlin_05_graph_two_linear_relations",
        "qlin_06_table_and_equation_graph",
        "qlin_07_missing_ordered_pair",
        "qlin_08_intersection_identification",
        "qlin_09_contextual_intersection",
        "qlin_10_graphical_simultaneous_equations",
        "qlin_11_context_to_graph_simultaneous_equations",
    ]

    mastery_question_id = (
        "qlin_12_table_graph_"
        "intersection_mastery"
    )

    session = engine.start_session(
        student_id=student_id,
        concept_id=GHANA_CONCEPT_ID,
    )

    assert session.progress.concept_mastered is False

    for question_id in expected_regular_questions:
        assert session.question is not None
        assert session.question.id == question_id

        submit_correct(
            engine=engine,
            student_id=student_id,
            concept_id=GHANA_CONCEPT_ID,
            question_id=question_id,
        )

        session = engine.get_session(
            student_id
        )

        assert session is not None
        assert session.progress.concept_mastered is False
        assert (
            GHANA_CONCEPT_ID
            not in session.mastered_concept_ids
        )

    assert session.progress.attempts == 11
    assert session.progress.evidence_score == 1.0

    assert session.question is not None
    assert session.question.id == mastery_question_id

    assert session.action == (
        ConceptDecisionAction.VERIFY_MASTERY
    )

    submit_correct(
        engine=engine,
        student_id=student_id,
        concept_id=GHANA_CONCEPT_ID,
        question_id=mastery_question_id,
    )

    session = engine.get_session(
        student_id
    )

    assert session is not None

    assert session.progress.attempts == 12
    assert session.progress.evidence_score == 1.0

    assert session.progress.concept_mastered is True

    assert (
        GHANA_CONCEPT_ID
        in session.mastered_concept_ids
    )

    assert session.question is None
    assert session.session_complete is True

    assert session.action == (
        ConceptDecisionAction.COMPLETE_CONCEPT
    )
