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


def test_diagnostic_error_triggers_remediation(
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
        == "remediate"
    )

    assert (
        decision.return_target_question_id
        == "Q1"
    )


def test_successful_remediation_returns_to_original(
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

    decision = engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q2",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    assert decision is not None

    assert (
        decision.question.question_id
        == "Q1"
    )

    assert (
        decision.decision_type
        == "reassess"
    )

    assert (
        decision.return_target_question_id
        == "Q1"
    )


def test_correct_reassessment_can_advance(
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

    engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q2",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    decision = engine.submit(
        learner_id=1,
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


def test_learner_state_records_remediation_cycle(
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

    assert learner.in_remediation

    assert (
        learner.remediation_return_question_id
        == "Q1"
    )

    assert (
        learner.remediation_question_id
        == "Q2"
    )

    engine.submit(
        learner_id=1,
        evidence=ResponseEvidence(
            question_id="Q2",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    assert not learner.in_remediation


def test_correct_first_answer_does_not_remediate(
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
        decision.decision_type
        == "advance"
    )

    assert (
        decision.return_target_question_id
        is None
    )
