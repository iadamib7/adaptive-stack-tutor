from backend.app.integrations.stack_xml.export_models import (
    StackQuestionInventory,
)
from backend.app.learning.curriculum_mapping.models import (
    CurriculumQuestionMap,
)


class CurriculumMappingValidator:
    def validate_question_ids(
        self,
        curriculum_map: CurriculumQuestionMap,
        inventory: StackQuestionInventory,
    ) -> list[str]:
        inventory_question_ids = {
            question.source_question_id
            for question in inventory.questions
            if question.source_question_id is not None
        }

        errors: list[str] = []

        for mapping in curriculum_map.mappings:
            for question in mapping.questions:
                if (
                    question.question_id
                    not in inventory_question_ids
                ):
                    errors.append(
                        f"Question {question.question_id} "
                        f"mapped to {mapping.concept_id} "
                        "does not exist in the inventory."
                    )

        return errors

    def find_unmapped_questions(
        self,
        curriculum_map: CurriculumQuestionMap,
        inventory: StackQuestionInventory,
    ) -> list[str]:
        mapped_question_ids = {
            question.question_id
            for mapping in curriculum_map.mappings
            for question in mapping.questions
        }

        return [
            question.source_question_id
            for question in inventory.questions
            if (
                question.source_question_id is not None
                and question.source_question_id
                not in mapped_question_ids
            )
        ]
