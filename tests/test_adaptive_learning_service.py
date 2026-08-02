from backend.app.learning.question_bank.question import (
    DifficultyLevel,
    Question,
)
from backend.app.learning.question_bank.repository import QuestionRepository
from backend.app.services.adaptive_learning_service import (
    AdaptiveLearningService,
)


def build_question(
    question_id: int,
    concept: str,
    difficulty: DifficultyLevel,
    correct_answer: str = "5x^4",
) -> Question:
    return Question(
        id=question_id,
        course="Calculus",
        topic="Differentiation",
        concept=concept,
        difficulty=difficulty,
        question_text="Differentiate f(x) = x^5.",
        correct_answer=correct_answer,
        prerequisite="Exponent Rules",
        learning_outcome=(
            f"Apply the {concept} correctly to differentiate "
            "a mathematical expression."
        ),
        common_errors=[
            "Forgetting to multiply by the original exponent.",
            "Forgetting to reduce the exponent by one.",
        ],
        remediation_concept="Exponent Rules",
        stack_identifier=f"question-{question_id}",
    )


def test_correct_attempt_updates_student() -> None:
    repository = QuestionRepository(
        [
            build_question(
                question_id=1,
                concept="Power Rule",
                difficulty=DifficultyLevel.BEGINNER,
            ),
            build_question(
                question_id=2,
                concept="Power Rule",
                difficulty=DifficultyLevel.EASY,
                correct_answer="7x^6",
            ),
        ]
    )

    service = AdaptiveLearningService(repository)

    result = service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="5x^4",
    )

    assert result.correct is True
    assert result.student_response == "5x^4"
    assert result.expected_answer == "5x^4"
    assert result.submitted_question_id == 1
    assert result.submitted_concept == "Power Rule"

    assert result.mastery_before == 0.5
    assert result.mastery_after > result.mastery_before

    assert result.student.id == 1
    assert result.student.name == "Test Student"
    assert result.student.mastery["Power Rule"] == result.mastery_after

    assert result.feedback
    assert "Correct" in result.feedback
    assert result.evaluation_error is None

    assert result.next_question is not None
    assert result.next_question.id == 2
    assert result.next_question.concept == "Power Rule"


def test_incorrect_attempt_reduces_mastery() -> None:
    repository = QuestionRepository(
        [
            build_question(
                question_id=1,
                concept="Product Rule",
                difficulty=DifficultyLevel.EASY,
                correct_answer="5x^4",
            ),
            build_question(
                question_id=2,
                concept="Product Rule",
                difficulty=DifficultyLevel.BEGINNER,
                correct_answer="3x^2",
            ),
        ]
    )

    service = AdaptiveLearningService(repository)

    result = service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="2x",
    )

    assert result.correct is False
    assert result.student_response == "2x"
    assert result.expected_answer == "5x^4"
    assert result.submitted_concept == "Product Rule"

    assert result.mastery_before == 0.5
    assert result.mastery_after < result.mastery_before
    assert result.concept_mastered is False

    assert result.feedback
    assert "not mathematically equivalent" in result.feedback
    assert "Product Rule" in result.feedback

    assert result.next_question is not None
    assert result.next_question.id == 2
    assert result.next_question.concept == "Product Rule"


def test_attempt_history_is_recorded() -> None:
    repository = QuestionRepository(
        [
            build_question(
                question_id=1,
                concept="Power Rule",
                difficulty=DifficultyLevel.BEGINNER,
            )
        ]
    )

    service = AdaptiveLearningService(repository)

    result = service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="5x^4",
    )

    history = service.get_attempt_history(student_id=1)

    assert len(history) == 1

    recorded_attempt = history[0]

    assert recorded_attempt.student_id == 1
    assert recorded_attempt.question_id == 1
    assert recorded_attempt.concept == "Power Rule"
    assert recorded_attempt.response == "5x^4"
    assert recorded_attempt.correct is True

    assert result.correct is True


def test_equivalent_expression_is_graded_correctly() -> None:
    repository = QuestionRepository(
        [
            build_question(
                question_id=1,
                concept="Power Rule",
                difficulty=DifficultyLevel.BEGINNER,
            )
        ]
    )

    service = AdaptiveLearningService(repository)

    result = service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="x^4 * 5",
    )

    assert result.correct is True
    assert result.evaluation_error is None


def test_malformed_expression_does_not_count_as_correct() -> None:
    repository = QuestionRepository(
        [
            build_question(
                question_id=1,
                concept="Power Rule",
                difficulty=DifficultyLevel.BEGINNER,
            )
        ]
    )

    service = AdaptiveLearningService(repository)

    result = service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="5x^^4",
    )

    assert result.correct is False
    assert result.evaluation_error is not None
    assert "could not be interpreted" in result.feedback


def test_unknown_question_raises_error() -> None:
    repository = QuestionRepository([])

    service = AdaptiveLearningService(repository)

    try:
        service.process_submission(
            student_id=1,
            student_name="Test Student",
            question_id=999,
            response="5x^4",
        )
    except ValueError as error:
        assert str(error) == "Question not found."
    else:
        raise AssertionError("Expected ValueError for an unknown question.")