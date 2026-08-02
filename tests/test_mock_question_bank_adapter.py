from backend.app.integrations.question_bank.mock_adapter import (
    MockQuestionBankAdapter,
)
from backend.app.integrations.question_bank.models import (
    CurriculumStage,
)


def test_get_question_by_id() -> None:
    adapter = MockQuestionBankAdapter()

    question = adapter.get_question("JHS-ALG-001")

    assert question is not None
    assert question.concept == "Linear Equations"
    assert question.curriculum_stage == CurriculumStage.JHS


def test_unknown_question_returns_none() -> None:
    adapter = MockQuestionBankAdapter()

    assert adapter.get_question("UNKNOWN") is None


def test_filter_questions_by_concept() -> None:
    adapter = MockQuestionBankAdapter()

    questions = adapter.find_questions(
        concept="Linear Equations",
    )

    assert len(questions) == 3
    assert all(
        question.concept == "Linear Equations"
        for question in questions
    )


def test_filter_questions_by_difficulty() -> None:
    adapter = MockQuestionBankAdapter()

    questions = adapter.find_questions(
        concept="Linear Equations",
        difficulty=2,
    )

    assert len(questions) == 1
    assert questions[0].id == "JHS-ALG-002"


def test_filter_questions_by_curriculum_stage() -> None:
    adapter = MockQuestionBankAdapter()

    questions = adapter.find_questions(
        curriculum_stage=CurriculumStage.SHS,
    )

    assert len(questions) == 1
    assert questions[0].concept == "Simultaneous Equations"


def test_question_contains_prerequisite_metadata() -> None:
    adapter = MockQuestionBankAdapter()

    question = adapter.get_question("JHS-ALG-002")

    assert question is not None
    assert "Integer Operations" in question.prerequisites
