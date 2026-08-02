import pytest

from backend.app.learning.assessment.answer_evaluator import (
    AnswerEvaluator,
)


@pytest.fixture
def evaluator() -> AnswerEvaluator:
    return AnswerEvaluator()


@pytest.mark.parametrize(
    "student_answer",
    [
        "5x^4",
        "5*x^4",
        "5*x**4",
        "x^4*5",
        "5(x^4)",
    ],
)
def test_equivalent_answers_are_correct(
    evaluator: AnswerEvaluator,
    student_answer: str,
) -> None:
    result = evaluator.evaluate(
        student_answer=student_answer,
        expected_answer="5x^4",
    )

    assert result.correct is True
    assert result.error_message is None


def test_incorrect_answer_is_rejected(
    evaluator: AnswerEvaluator,
) -> None:
    result = evaluator.evaluate(
        student_answer="x^4",
        expected_answer="5x^4",
    )

    assert result.correct is False


def test_empty_answer_is_rejected(
    evaluator: AnswerEvaluator,
) -> None:
    result = evaluator.evaluate(
        student_answer="",
        expected_answer="5x^4",
    )

    assert result.correct is False
    assert result.error_message == "No answer was provided."


def test_malformed_answer_returns_helpful_error(
    evaluator: AnswerEvaluator,
) -> None:
    result = evaluator.evaluate(
        student_answer="5x^^4",
        expected_answer="5x^4",
    )

    assert result.correct is False
    assert result.error_message is not None