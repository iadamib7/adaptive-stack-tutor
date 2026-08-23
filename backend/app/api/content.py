from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.app.content.ingestion.numbas.parser import (
    NumbasExamParser,
)

router = APIRouter(
    prefix="/content",
    tags=["Learner Content"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

NUMBAS_DIR = (
    PROJECT_ROOT
    / "resources"
    / "raw"
    / "numbas"
)

parser = NumbasExamParser()


def _question_files() -> list[Path]:
    return sorted(
        NUMBAS_DIR.glob("question-*.exam")
    )


def _question_id(path: Path) -> str:
    return path.name.split("-")[1]


def _part_payload(
    part: dict,
    index: int,
) -> dict:
    gaps = part.get(
        "gaps",
        [],
    )

    return {
        "index": index,
        "type": part.get(
            "type",
            "",
        ),
        "marks": part.get(
            "marks",
            0,
        ),
        "prompt": part.get(
            "prompt",
            "",
        ),
        "gap_count": len(gaps),
    }


@router.get("/numbas")
def get_numbas_questions() -> list[dict]:
    questions = []

    for path in _question_files():
        try:
            question = parser.parse(path)
        except Exception:
            continue

        questions.append(
            {
                "id": _question_id(path),
                "title": question.name,
                "provider": "Numbas",
                "filename": path.name,
                "licence": question.licence,
                "contributors": list(
                    question.contributors
                ),
                "part_count": len(
                    question.parts
                ),
            }
        )

    return questions


@router.get("/numbas/{question_id}")
def get_numbas_question(
    question_id: str,
) -> dict:
    for path in _question_files():
        if _question_id(path) != question_id:
            continue

        question = parser.parse(path)

        return {
            "id": question_id,
            "title": question.name,
            "provider": "Numbas",
            "filename": path.name,
            "statement": question.statement,
            "description": question.description,
            "advice": question.advice,
            "licence": question.licence,
            "contributors": list(
                question.contributors
            ),
            "tags": list(
                question.tags
            ),
            "parts": [
                _part_payload(
                    part,
                    index,
                )
                for index, part in enumerate(
                    question.parts,
                    start=1,
                )
            ],
        }

    raise HTTPException(
        status_code=404,
        detail="Numbas question not found.",
    )
