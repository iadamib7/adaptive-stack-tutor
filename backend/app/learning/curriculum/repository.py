from backend.app.learning.curriculum.models import (
    CurriculumConcept,
    CurriculumMap,
)


class CurriculumRepository:
    def __init__(
        self,
        curriculum_map: CurriculumMap,
    ) -> None:
        self.curriculum_map = curriculum_map

        self._concepts_by_id = {
            concept.id: concept
            for concept in curriculum_map.concepts
        }

    def get_concept(
        self,
        concept_id: str,
    ) -> CurriculumConcept | None:
        return self._concepts_by_id.get(concept_id)

    def get_all_concepts(
        self,
    ) -> list[CurriculumConcept]:
        return self.curriculum_map.concepts.copy()

    def get_concepts_by_level(
        self,
        level_id: str,
    ) -> list[CurriculumConcept]:
        normalized_level = level_id.casefold()

        return [
            concept
            for concept in self.curriculum_map.concepts
            if concept.level_id.casefold() == normalized_level
        ]

    def get_prerequisites(
        self,
        concept_id: str,
    ) -> list[CurriculumConcept]:
        concept = self.get_concept(concept_id)

        if concept is None:
            return []

        return [
            prerequisite
            for prerequisite_id in (
                concept.prerequisite_concept_ids
            )
            if (
                prerequisite := self.get_concept(
                    prerequisite_id
                )
            )
            is not None
        ]

    def get_next_concepts(
        self,
        concept_id: str,
    ) -> list[CurriculumConcept]:
        concept = self.get_concept(concept_id)

        if concept is None:
            return []

        return [
            next_concept
            for next_concept_id in concept.next_concept_ids
            if (
                next_concept := self.get_concept(
                    next_concept_id
                )
            )
            is not None
        ]

    def get_questions_for_concept(
        self,
        concept_id: str,
    ) -> list[str]:
        concept = self.get_concept(concept_id)

        if concept is None:
            return []

        return concept.stack_question_ids.copy()

    def get_ordered_pathway(
        self,
    ) -> list[CurriculumConcept]:
        return sorted(
            self.curriculum_map.concepts,
            key=lambda concept: (
                concept.progression_order,
                concept.id,
            ),
        )
