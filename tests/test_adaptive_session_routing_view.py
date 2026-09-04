from backend.app.learning.adaptive_engine.models import (
    AdaptiveDecision,
    AdaptiveQuestion,
    CandidateScore,
)

from backend.app.learning.adaptive_engine.session_service import (
    AdaptiveSessionView,
)


def test_session_view_can_expose_remediation_route(
) -> None:
    view = AdaptiveSessionView(
        learner_id=1,
        question_id="Q2",
        title="Sign support",
        seed=123,
        html="<p>Support</p>",
        inputs={},
        ability=-0.2,
        decision_reason=(
            "Diagnostic evidence "
            "'sign_error' triggered remediation."
        ),
        decision_type="remediate",
        return_target_question_id="Q1",
        previous_score=0.0,
        previous_outcome="sign_error",
    )

    assert (
        view.decision_type
        == "remediate"
    )

    assert (
        view.return_target_question_id
        == "Q1"
    )

    assert (
        view.previous_outcome
        == "sign_error"
    )


def test_session_view_can_expose_reassessment_route(
) -> None:
    view = AdaptiveSessionView(
        learner_id=1,
        question_id="Q1",
        title="Initial equation",
        seed=456,
        html="<p>Retry</p>",
        inputs={},
        ability=0.0,
        decision_reason=(
            "Remediation completed."
        ),
        decision_type="reassess",
        return_target_question_id="Q1",
        previous_score=1.0,
        previous_outcome="correct",
    )

    assert (
        view.decision_type
        == "reassess"
    )

    assert (
        view.question_id
        == "Q1"
    )

    assert (
        view.return_target_question_id
        == "Q1"
    )


def test_adaptive_decision_defaults_remain_compatible(
) -> None:
    question = AdaptiveQuestion(
        question_id="Q1",
        title="Question 1",
    )

    score = CandidateScore(
        question_id="Q1",
        total=1.0,
        difficulty_match=1.0,
        diagnostic_match=0.0,
        novelty_bonus=0.0,
        repetition_penalty=0.0,
    )

    decision = AdaptiveDecision(
        question=question,
        score=score,
        reason="Normal progression.",
    )

    assert (
        decision.decision_type
        == "advance"
    )

    assert (
        decision.return_target_question_id
        is None
    )
