from backend.app.learning.question_bank.question import (
    DifficultyLevel,
    Question,
)
from backend.app.learning.question_bank.repository import QuestionRepository
from backend.app.learning.recommendation.engine import RecommendationEngine
from backend.app.learning.student_model.student import Student


def build_question(
    question_id: int,
    concept: str,
    difficulty: DifficultyLevel,
    course: str = "Calculus",
) -> Question:
    return Question(
        id=question_id,
        course=course,
        topic="Test Topic",
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


def test_recommends_weakest_concept() -> None:
    questions = [
        build_question(
            question_id=1,
            concept="Power Rule",
            difficulty=DifficultyLevel.ADVANCED,
        ),
        build_question(
            question_id=2,
            concept="Product Rule",
            difficulty=DifficultyLevel.EASY,
        ),
    ]

    repository = QuestionRepository(questions)
    engine = RecommendationEngine(repository)

    student = Student(
        id=1,
        name="Test Student",
        mastery={
            "Power Rule": 0.80,
            "Product Rule": 0.30,
        },
    )

    recommendation = engine.recommend_next_question(student)

    assert recommendation is not None
    assert recommendation.target_concept == "Product Rule"
    assert recommendation.question.id == 2


def test_avoids_attempted_question_when_possible() -> None:
    questions = [
        build_question(
            question_id=1,
            concept="Power Rule",
            difficulty=DifficultyLevel.EASY,
        ),
        build_question(
            question_id=2,
            concept="Power Rule",
            difficulty=DifficultyLevel.EASY,
        ),
    ]

    repository = QuestionRepository(questions)
    engine = RecommendationEngine(repository)

    student = Student(
        id=1,
        name="Test Student",
        mastery={"Power Rule": 0.40},
    )

    recommendation = engine.recommend_next_question(
        student=student,
        attempted_question_ids={1},
    )

    assert recommendation is not None
    assert recommendation.question.id == 2


def test_recommends_beginner_content_for_new_student() -> None:
    questions = [
        build_question(
            question_id=1,
            concept="Power Rule",
            difficulty=DifficultyLevel.BEGINNER,
        ),
        build_question(
            question_id=2,
            concept="Product Rule",
            difficulty=DifficultyLevel.INTERMEDIATE,
        ),
    ]

    repository = QuestionRepository(questions)
    engine = RecommendationEngine(repository)

    student = Student(
        id=1,
        name="New Student",
    )

    recommendation = engine.recommend_next_question(student)

    assert recommendation is not None
    assert recommendation.question.id == 1