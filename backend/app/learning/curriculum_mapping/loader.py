from pathlib import Path

from backend.app.learning.curriculum_mapping.models import (
    CurriculumQuestionMap,
)


def load_curriculum_question_map(
    path: Path,
) -> CurriculumQuestionMap:
    if not path.is_file():
        raise FileNotFoundError(
            f"Curriculum question map was not found: "
            f"{path}"
        )

    try:
        return (
            CurriculumQuestionMap.model_validate_json(
                path.read_text(encoding="utf-8")
            )
        )
    except ValueError as error:
        raise ValueError(
            f"Curriculum question map is not valid: "
            f"{path}"
        ) from error
