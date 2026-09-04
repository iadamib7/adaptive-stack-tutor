from backend.app.learning.adaptive_engine.engine import (
    CurriculumIndependentAdaptiveEngine,
)

from backend.app.learning.adaptive_engine.models import (
    AdaptiveQuestion,
    ResponseEvidence,
)


def _scrambled_questions() -> list[
    AdaptiveQuestion
]:
    # Deliberately NOT pedagogical order.
    #
    # If the engine followed list/XML order,
    # it would start at Q5.
    return [
        AdaptiveQuestion(
            question_id="Q5",
            title="Unrelated advanced item",
            difficulty=1.0,
            skills=(
                "advanced_extension",
            ),
            prerequisites=(
                "advanced_ready",
            ),
        ),
        AdaptiveQuestion(
            question_id="Q3",
            title="Next function challenge",
            difficulty=0.2,
            skills=(
                "advanced_ready",
            ),
            prerequisites=(
                "function_interpretation",
            ),
        ),
        AdaptiveQuestion(
            question_id="Q1",
            title="Entry function question",
            difficulty=0.0,
            entry_point=True,
            skills=(
                "function_interpretation",
            ),
            diagnoses=(
                "sign_error",
            ),
        ),
        AdaptiveQuestion(
            question_id="Q4",
            title="Another later item",
            difficulty=0.8,
            prerequisites=(
                "advanced_ready",
            ),
        ),
        AdaptiveQuestion(
            question_id="Q2",
            title="Targeted sign support",
            difficulty=-0.2,
            supports=(
                "sign_error",
            ),
        ),
    ]


def test_xml_or_list_order_does_not_control_start(
) -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            _scrambled_questions()
        )
    )

    decision = engine.start(
        learner_id=1
    )

    assert decision is not None

    # Q5 is first in input order.
    # Q1 must still be selected because it is
    # the bank-local entry point.
    assert (
        decision.question.question_id
        == "Q1"
    )

    assert (
        decision.decision_type
        == "start"
    )


def test_correct_entry_response_unlocks_next_skill(
) -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            _scrambled_questions()
        )
    )

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

    # Q3 requires the skill taught/tested by Q1.
    assert (
        decision.question.question_id
        == "Q3"
    )

    learner = (
        engine.get_or_create_learner(
            2
        )
    )

    assert (
        "function_interpretation"
        in learner.mastered_skills
    )


def test_unmet_prerequisite_blocks_advanced_item(
) -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            _scrambled_questions()
        )
    )

    engine.start(
        learner_id=3
    )

    decision = engine.submit(
        learner_id=3,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    assert decision is not None

    assert (
        decision.question.question_id
        != "Q5"
    )

    assert (
        decision.question.question_id
        != "Q4"
    )


def test_diagnostic_error_branches_to_support(
) -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            _scrambled_questions()
        )
    )

    engine.start(
        learner_id=4
    )

    decision = engine.submit(
        learner_id=4,
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


def test_two_learners_take_different_paths_from_same_q1(
) -> None:
    questions = _scrambled_questions()

    mastery_engine = (
        CurriculumIndependentAdaptiveEngine(
            questions
        )
    )

    support_engine = (
        CurriculumIndependentAdaptiveEngine(
            questions
        )
    )

    mastery_engine.start(
        learner_id=10
    )

    support_engine.start(
        learner_id=11
    )

    mastery_next = mastery_engine.submit(
        learner_id=10,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=1.0,
            prt_outcome="correct",
        ),
    )

    support_next = support_engine.submit(
        learner_id=11,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    assert mastery_next is not None
    assert support_next is not None

    assert (
        mastery_next.question.question_id
        == "Q3"
    )

    assert (
        support_next.question.question_id
        == "Q2"
    )

    assert (
        mastery_next.question.question_id
        != support_next.question.question_id
    )


def test_successful_support_returns_to_entry_question(
) -> None:
    engine = (
        CurriculumIndependentAdaptiveEngine(
            _scrambled_questions()
        )
    )

    engine.start(
        learner_id=20
    )

    engine.submit(
        learner_id=20,
        evidence=ResponseEvidence(
            question_id="Q1",
            score=0.0,
            prt_outcome="sign_error",
        ),
    )

    decision = engine.submit(
        learner_id=20,
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
