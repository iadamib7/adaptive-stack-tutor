from backend.app.learning.knowledge_graph.models import (
    KnowledgeConcept,
)

from backend.app.learning.knowledge_graph.repository import (
    KnowledgeGraphRepository,
)


class AdaptiveConceptSelector:
    """
    Deterministic concept-level pathway selector.

    Uses the knowledge graph as the source of truth for
    prerequisite, remediation, and progression relationships.

    When deliverable_concept_ids is provided, concepts remain
    visible for prerequisite reasoning but only deliverable
    concepts may become active learner destinations.
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphRepository,
        deliverable_concept_ids: (
            set[str] | None
        ) = None,
    ) -> None:
        self.knowledge_graph = knowledge_graph

        self.deliverable_concept_ids = (
            None
            if deliverable_concept_ids is None
            else set(
                deliverable_concept_ids
            )
        )

    def _is_deliverable(
        self,
        concept_id: str,
    ) -> bool:
        if (
            self.deliverable_concept_ids
            is None
        ):
            return True

        return (
            concept_id
            in self.deliverable_concept_ids
        )

    def select_starting_concept(
        self,
        mastered_concept_ids: set[str],
    ) -> KnowledgeConcept | None:
        eligible = (
            self.knowledge_graph
            .eligible_concepts(
                mastered_concept_ids
            )
        )

        for concept in eligible:
            if self._is_deliverable(
                concept.concept_id
            ):
                return concept

        return None

    def select_next_concept(
        self,
        current_concept_id: str,
        mastered_concept_ids: set[str],
    ) -> KnowledgeConcept | None:
        extensions = (
            self.knowledge_graph
            .extensions_for(
                current_concept_id
            )
        )

        eligible_ids = {
            concept.concept_id
            for concept
            in self.knowledge_graph
            .eligible_concepts(
                mastered_concept_ids
            )
        }

        for concept in extensions:
            if (
                concept.concept_id
                in eligible_ids
                and self._is_deliverable(
                    concept.concept_id
                )
            ):
                return concept

        return self.select_starting_concept(
            mastered_concept_ids
        )

    def select_remediation_concept(
        self,
        current_concept_id: str,
        mastered_concept_ids: set[str],
    ) -> KnowledgeConcept | None:
        remediation = (
            self.knowledge_graph
            .remediation_for(
                current_concept_id
            )
        )

        for concept in remediation:
            if (
                concept.concept_id
                not in mastered_concept_ids
                and self._is_deliverable(
                    concept.concept_id
                )
            ):
                return concept

        return None
