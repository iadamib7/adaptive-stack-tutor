from backend.app.learning.curriculum_mapping.models import (
    ConceptQuestionMapping,
    CurriculumQuestionMap,
    QuestionEvidence,
)


class CurriculumMappingRepository:
    def __init__(
        self,
        curriculum_question_map: CurriculumQuestionMap,
    ) -> None:
        self.curriculum_question_map = (
            curriculum_question_map
        )

        self._mappings_by_concept = {
            mapping.concept_id: mapping
            for mapping in curriculum_question_map.mappings
        }

        self._question_to_concept: dict[
            str,
            ConceptQuestionMapping,
        ] = {}

        for mapping in curriculum_question_map.mappings:
            for question in mapping.questions:
                if question.question_id in (
                    self._question_to_concept
                ):
                    raise ValueError(
                        "Question "
                        f"{question.question_id} is mapped "
                        "to more than one concept."
                    )

                self._question_to_concept[
                    question.question_id
                ] = mapping

    def get_mapping(
        self,
        concept_id: str,
    ) -> ConceptQuestionMapping | None:
        return self._mappings_by_concept.get(concept_id)

    def get_all_mappings(
        self,
    ) -> list[ConceptQuestionMapping]:
        return (
            self.curriculum_question_map.mappings.copy()
        )

    def get_questions_for_concept(
        self,
        concept_id: str,
    ) -> list[QuestionEvidence]:
        mapping = self.get_mapping(concept_id)

        if mapping is None:
            return []

        return sorted(
            mapping.questions,
            key=lambda question: (
                question.sequence_order,
                question.question_id,
            ),
        )

    def get_concept_for_question(
        self,
        question_id: str,
    ) -> ConceptQuestionMapping | None:
        return self._question_to_concept.get(
            question_id
        )

    def get_mastery_questions(
        self,
        concept_id: str,
    ) -> list[QuestionEvidence]:
        return [
            question
            for question in self.get_questions_for_concept(
                concept_id
            )
            if question.required_for_mastery
        ]
