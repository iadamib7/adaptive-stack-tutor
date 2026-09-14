from backend.app.learning.adaptive_engine.engine import (
    CurriculumIndependentAdaptiveEngine,
)

from backend.app.learning.adaptive_engine.models import (
    AdaptiveQuestion,
    ResponseEvidence,
)


def _engine() -> (
    CurriculumIndependentAdaptiveEngine
):
    return CurriculumIndependentAdaptiveEngine(
        [
            AdaptiveQuestion(
                question_id="Q1",
                title="Initial equation",
                difficulty=0.0,
                diagnoses=(
                    "sign_error",
                ),
            ),
            AdaptiveQuestion(
                question_id="Q2",
                title="Sign support",
                difficulty=-0.2,
                supports=(
                    "sign_error",
                ),
            ),
            AdaptiveQuestion(
                question_id="Q3",
                title="Next challenge",
                difficulty=0.2,
            ),
        ]
    )


def test_session_starts_normally() -> None:
    engine = _engine()

    decision = engine.start(
        learner_id=1
    )

    assert decision is not None

    assert (
        decision.question.question_id
        == "Q1"
    )

    assert (
        decision.decision_type
        == "start"
    )


def test_diagnostic_error_can_branch_to_support(
) -> None:
    engine = _engine()

    engine.start(
        learner_id=1
    )

    decision = engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    assert decision is not None

    assert (
        decision.question.question_id
        == "Q2"
    )

    assert (
        decision.decision_type
        == "support"
    )

    assert (
        decision.return_target_question_id
        is None
    )


def test_successful_support_does_not_force_reassessment(
) -> None:
    engine = _engine()

    engine.start(
        learner_id=1
    )

    support = engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    assert support is not None

    assert (
        support.question.question_id
        == "Q2"
    )

    decision = engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q2",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    assert decision is not None

    # The selector runs normally after support.
    # It is not forced back to Q1.
    assert (
        decision.question.question_id
        == "Q3"
    )

    assert (
        decision.decision_type
        == "advance"
    )

    assert (
        decision.return_target_question_id
        is None
    )


def test_support_completion_clears_diagnostic_need(
) -> None:
    engine = _engine()

    engine.start(
        learner_id=1
    )

    engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    learner = (
        engine.get_or_create_learner(
            1
        )
    )

    assert (
        learner.misconception_counts.get(
            "sign_error"
        )
        == 1
    )

    engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q2",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    assert (
        "sign_error"
        not in learner.misconception_counts
    )

    assert not learner.in_remediation


def test_correct_first_answer_takes_general_path(
) -> None:
    engine = _engine()

    engine.start(
        learner_id=2
    )

    decision = engine.submit(
        learner_id=2,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    assert decision is not None

    assert (
        decision.question.question_id
        == "Q3"
    )

    assert (
        decision.decision_type
        == "advance"
    )

    assert (
        decision.return_target_question_id
        is None
    )


def test_same_response_state_is_deterministic(
) -> None:
    engine_a = _engine()
    engine_b = _engine()

    engine_a.start(
        learner_id=10
    )

    engine_b.start(
        learner_id=10
    )

    decision_a = engine_a.submit(
        learner_id=10,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    decision_b = engine_b.submit(
        learner_id=10,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    assert decision_a is not None
    assert decision_b is not None

    assert (
        decision_a.question.question_id
        == decision_b.question.question_id
        == "Q2"
    )

    assert (
        decision_a.decision_type
        == decision_b.decision_type
        == "support"
    )


def test_different_responses_create_different_paths(
) -> None:
    success_engine = _engine()
    support_engine = _engine()

    success_engine.start(
        learner_id=20
    )

    support_engine.start(
        learner_id=21
    )

    success_next = (
        success_engine.submit(
            learner_id=20,
            evidence=ResponseEvidence(
                question_id="Q1",
                score=1.0,
                prt_outcome="correct",
            ),
        )
    )

    support_next = (
        support_engine.submit(
            learner_id=21,
            evidence=ResponseEvidence(
                question_id="Q1",
                score=0.0,
                prt_outcome="sign_error",
            ),
        )
    )

    assert success_next is not None
    assert support_next is not None

    assert (
        success_next.question.question_id
        == "Q3"
    )

    assert (
        support_next.question.question_id
        == "Q2"
    )

    assert (
        success_next.question.question_id
        != support_next.question.question_id
    )
