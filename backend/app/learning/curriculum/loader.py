from pathlib import Path

from backend.app.learning.curriculum.models import (
    CurriculumMap,
)


def load_curriculum_map(
    path: Path,
) -> CurriculumMap:
    if not path.is_file():
        raise FileNotFoundError(
            f"Curriculum map was not found: {path}"
        )

    try:
        content = path.read_text(encoding="utf-8")

        return CurriculumMap.model_validate_json(
            content
        )
    except ValueError as error:
        raise ValueError(
            f"Curriculum map is not valid: {path}"
        ) from error
