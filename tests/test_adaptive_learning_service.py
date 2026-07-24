from backend.app.learning.question_bank.question import (
    DifficultyLevel,
    Question,
)
from backend.app.learning.question_bank.repository import (
    QuestionRepository,
)
from backend.app.services.adaptive_learning_service import (
    AdaptiveLearningService,
)


def build_question(
    question_id: int,
    concept: str,
    difficulty: DifficultyLevel,
) -> Question:
    return Question(
        id=question_id,
        course="Calculus",
        topic="Differentiation",
        concept=concept,
        difficulty=difficulty,
        question_text=f"Question {question_id}",
        correct_answer="Answer",
        prerequisite=None,
        learning_outcome="Test learning outcome",
        common_errors=[],
        remediation_concept=None,
        stack_identifier=None,
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
            ),
        ]
    )

    service = AdaptiveLearningService(repository)

    result = service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="5x^4",
        correct=True,
    )

    assert result.student.attempts == 1
    assert result.student.correct == 1
    assert result.student.incorrect == 0
    assert result.mastery_before == 0.5
    assert result.mastery_after == 0.6
    assert result.next_question is not None
    assert result.next_question.id == 2


def test_incorrect_attempt_reduces_mastery() -> None:
    repository = QuestionRepository(
        [
            build_question(
                question_id=1,
                concept="Product Rule",
                difficulty=DifficultyLevel.EASY,
            )
        ]
    )

    service = AdaptiveLearningService(repository)

    result = service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="2x",
        correct=False,
    )

    assert result.student.attempts == 1
    assert result.student.correct == 0
    assert result.student.incorrect == 1
    assert result.mastery_after == 0.4


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

    service.process_submission(
        student_id=1,
        student_name="Test Student",
        question_id=1,
        response="5x^4",
        correct=True,
    )

    history = service.get_attempt_history(1)

    assert len(history) == 1
    assert history[0].question_id == 1
    assert history[0].correct is True