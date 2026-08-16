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
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphRepository,
    ) -> None:
        self.knowledge_graph = knowledge_graph

    def select_starting_concept(
        self,
        mastered_concept_ids: set[str],
    ) -> KnowledgeConcept | None:
        eligible = self.knowledge_graph.eligible_concepts(
            mastered_concept_ids
        )

        if not eligible:
            return None

        return eligible[0]

    def select_next_concept(
        self,
        current_concept_id: str,
        mastered_concept_ids: set[str],
    ) -> KnowledgeConcept | None:
        extensions = self.knowledge_graph.extensions_for(
            current_concept_id
        )

        eligible_ids = {
            concept.concept_id
            for concept
            in self.knowledge_graph.eligible_concepts(
                mastered_concept_ids
            )
        }

        for concept in extensions:
            if concept.concept_id in eligible_ids:
                return concept

        return self.select_starting_concept(
            mastered_concept_ids
        )

    def select_remediation_concept(
        self,
        current_concept_id: str,
        mastered_concept_ids: set[str],
    ) -> KnowledgeConcept | None:
        remediation = self.knowledge_graph.remediation_for(
            current_concept_id
        )

        for concept in remediation:
            if (
                concept.concept_id
                not in mastered_concept_ids
            ):
                return concept

        return None