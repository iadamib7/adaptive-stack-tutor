from backend.app.learning.adaptive_engine import (
    AdaptiveQuestion,
    CurriculumIndependentAdaptiveEngine,
    ResponseEvidence,
)


def build_questions() -> list[AdaptiveQuestion]:
    return [
        AdaptiveQuestion(
            question_id="Q1",
            title="Diagnostic entry question",
            difficulty=0.0,
        ),
        AdaptiveQuestion(
            question_id="Q2",
            title="Sign-error remediation",
            difficulty=-0.4,
            supports=(
                "sign_error",
            ),
        ),
        AdaptiveQuestion(
            question_id="Q3",
            title="Distribution remediation",
            difficulty=-0.4,
            supports=(
                "distribution_error",
            ),
        ),
        AdaptiveQuestion(
            question_id="Q4",
            title="Moderate practice",
            difficulty=0.4,
        ),
        AdaptiveQuestion(
            question_id="Q5",
            title="Advanced practice",
            difficulty=0.8,
        ),
    ]


def test_engine_requires_no_curriculum() -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            build_questions()
        )
    )

    decision = engine.start(
        learner_id=1
    )

    assert decision is not None
    assert decision.question.question_id == "Q1"


def test_correct_response_moves_upward() -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            build_questions()
        )
    )

    first = engine.start(
        learner_id=10
    )

    assert first is not None
    assert first.question.question_id == "Q1"

    next_decision = engine.submit(
        learner_id=10,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    assert next_decision is not None

    assert (
        next_decision.question.question_id
        == "Q4"
    )


def test_sign_error_branches_to_remediation() -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            build_questions()
        )
    )

    engine.start(
        learner_id=20
    )

    next_decision = engine.submit(
        learner_id=20,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    assert next_decision is not None

    assert (
        next_decision.question.question_id
        == "Q2"
    )


def test_distribution_error_branches_differently() -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            build_questions()
        )
    )

    engine.start(
        learner_id=30
    )

    next_decision = engine.submit(
        learner_id=30,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome=(
                "distribution_error"
            ),
        ),
    )

    assert next_decision is not None

    assert (
        next_decision.question.question_id
        == "Q3"
    )


def test_identical_state_is_deterministic() -> None:
    questions = build_questions()

    engine_a = (
        CurriculumIndependentAdaptiveEngine(
            questions
        )
    )

    engine_b = (
        CurriculumIndependentAdaptiveEngine(
            questions
        )
    )

    evidence = ResponseEvidence(
        question_id="Q1",
        score=0.0,
        prt_outcome="sign_error",
    )

    engine_a.start(
        learner_id=100
    )

    engine_b.start(
        learner_id=100
    )

    decision_a = engine_a.submit(
        learner_id=100,
        evidence=evidence,
    )

    decision_b = engine_b.submit(
        learner_id=100,
        evidence=evidence,
    )

    assert decision_a is not None
    assert decision_b is not None

    assert (
        decision_a.question.question_id
        == decision_b.question.question_id
    )

    assert (
        decision_a.score.total
        == decision_b.score.total
    )


def test_different_evidence_creates_non_linear_paths() -> None:
    questions = build_questions()

    sign_engine = (
        CurriculumIndependentAdaptiveEngine(
            questions
        )
    )

    distribution_engine = (
        CurriculumIndependentAdaptiveEngine(
            questions
        )
    )

    sign_engine.start(
        learner_id=201
    )

    distribution_engine.start(
        learner_id=202
    )

    sign_next = sign_engine.submit(
        learner_id=201,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    distribution_next = (
        distribution_engine.submit(
            learner_id=202,
            evidence=ResponseEvidence(
                question_id="Q1",
                score=0.0,
                prt_outcome=(
                    "distribution_error"
                ),
            ),
        )
    )

    assert sign_next is not None
    assert distribution_next is not None

    assert (
        sign_next.question.question_id
        == "Q2"
    )

    assert (
        distribution_next.question.question_id
        == "Q3"
    )
