import json
from pathlib import Path

from backend.app.integrations.stack_xml.export_models import (
    StackQuestionInventory,
)
from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.learning.curriculum_mapping.validator import (
    CurriculumMappingValidator,
)


MAP_PATH = Path(
    "examples/curriculum_mapping/"
    "kenya_grade9_integer_operations.json"
)

INVENTORY_PATH = Path(
    "resources/generated/kenya/grade9/"
    "grade9_questions_inventory.json"
)


def load_inventory() -> StackQuestionInventory:
    content = json.loads(
        INVENTORY_PATH.read_text(
            encoding="utf-8"
        )
    )

    return StackQuestionInventory.model_validate(
        content
    )


def test_all_mapped_questions_exist_in_inventory() -> None:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    inventory = load_inventory()

    errors = (
        CurriculumMappingValidator()
        .validate_question_ids(
            curriculum_map=curriculum_map,
            inventory=inventory,
        )
    )

    assert errors == []


def test_unmapped_inventory_questions_are_reported() -> None:
    curriculum_map = load_curriculum_question_map(
        MAP_PATH
    )

    inventory = load_inventory()

    unmapped = (
        CurriculumMappingValidator()
        .find_unmapped_questions(
            curriculum_map=curriculum_map,
            inventory=inventory,
        )
    )

    assert len(unmapped) == 74
    assert "207582" not in unmapped
    assert "207630" not in unmapped
