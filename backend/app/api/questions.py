from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from backend.app.learning.question_bank.loader import load_questions
from backend.app.learning.question_bank.question import (
    DifficultyLevel,
    Question,
)
from backend.app.learning.question_bank.repository import (
    QuestionRepository,
)

router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
QUESTION_FILE = PROJECT_ROOT / "datasets" / "questions.json"

repository = QuestionRepository(load_questions(QUESTION_FILE))


@router.get("", response_model=list[Question])
def get_questions(
    course: str | None = None,
    topic: str | None = None,
    concept: str | None = None,
    difficulty: DifficultyLevel | None = Query(default=None),
    prerequisite: str | None = None,
) -> list[Question]:
    return repository.filter_questions(
        course=course,
        topic=topic,
        concept=concept,
        difficulty=difficulty,
        prerequisite=prerequisite,
    )


@router.get("/{question_id}", response_model=Question)
def get_question(question_id: int) -> Question:
    question = repository.get_by_id(question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found.",
        )

    return question