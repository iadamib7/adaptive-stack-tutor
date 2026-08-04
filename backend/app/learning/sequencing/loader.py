from pathlib import Path

from backend.app.learning.sequencing.models import SequencingMap


def load_sequencing_map(path: Path) -> SequencingMap:
    if not path.exists():
        raise FileNotFoundError(
            f"Sequencing map was not found: {path}"
        )

    try:
        content = path.read_text(encoding="utf-8")
        return SequencingMap.model_validate_json(content)
    except ValueError as error:
        raise ValueError(
            f"Sequencing map is not valid: {path}"
        ) from error
