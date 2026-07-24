import json
from pathlib import Path

from .question import Question


def load_questions(file_path: Path) -> list[Question]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Question bank file was not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        raw_questions = json.load(file)

    if not isinstance(raw_questions, list):
        raise ValueError(
            "Question bank must contain a JSON list of questions."
        )

    return [
        Question.model_validate(question_data)
        for question_data in raw_questions
    ]