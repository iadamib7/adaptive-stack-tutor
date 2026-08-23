from __future__ import annotations

from collections.abc import Iterable

from backend.app.learning.knowledge_graph.models import (
    KnowledgeConcept,
)


class KnowledgeGraphRepository:
    """
    Read-only repository for curriculum-agnostic
    knowledge concepts.
    """

    def __init__(
        self,
        concepts: Iterable[
            KnowledgeConcept
        ],
    ) -> None:
        self._concepts: dict[
            str,
            KnowledgeConcept,
        ] = {}

        for concept in concepts:
            if (
                concept.concept_id
                in self._concepts
            ):
                raise ValueError(
                    "Duplicate knowledge concept ID: "
                    f"{concept.concept_id}"
                )

            self._concepts[
                concept.concept_id
            ] = concept

    def get(
        self,
        concept_id: str,
    ) -> KnowledgeConcept | None:
        return self._concepts.get(
            concept_id
        )

    def require(
        self,
        concept_id: str,
    ) -> KnowledgeConcept:
        concept = self.get(
            concept_id
        )

        if concept is None:
            raise ValueError(
                "Unknown knowledge concept: "
                f"{concept_id}"
            )

        return concept

    def all_concepts(
        self,
    ) -> list[KnowledgeConcept]:
        return list(
            self._concepts.values()
        )

    def prerequisites_for(
        self,
        concept_id: str,
    ) -> list[KnowledgeConcept]:
        concept = self.require(
            concept_id
        )

        return [
            self.require(
                prerequisite_id
            )
            for prerequisite_id
            in concept.prerequisite_concept_ids
        ]

    def direct_dependents_of(
        self,
        concept_id: str,
    ) -> list[KnowledgeConcept]:
        self.require(
            concept_id
        )

        return [
            concept
            for concept
            in self._concepts.values()
            if concept_id
            in concept.prerequisite_concept_ids
        ]

    def remediation_for(
        self,
        concept_id: str,
    ) -> list[KnowledgeConcept]:
        concept = self.require(
            concept_id
        )

        return [
            self.require(
                remediation_id
            )
            for remediation_id
            in concept.remediation_concept_ids
        ]

    def extensions_for(
        self,
        concept_id: str,
    ) -> list[KnowledgeConcept]:
        concept = self.require(
            concept_id
        )

        return [
            self.require(
                extension_id
            )
            for extension_id
            in concept.extension_concept_ids
        ]

    def eligible_concepts(
        self,
        mastered_concept_ids: set[str],
    ) -> list[KnowledgeConcept]:
        """
        Return concepts whose prerequisites are mastered
        but which have not themselves been mastered.
        """

        eligible: list[
            KnowledgeConcept
        ] = []

        for concept in (
            self._concepts.values()
        ):
            if (
                concept.concept_id
                in mastered_concept_ids
            ):
                continue

            prerequisites = set(
                concept.prerequisite_concept_ids
            )

            if prerequisites.issubset(
                mastered_concept_ids
            ):
                eligible.append(
                    concept
                )

        return eligible

    def descendants_of(
        self,
        concept_id: str,
    ) -> list[KnowledgeConcept]:
        self.require(
            concept_id
        )

        visited: set[str] = set()
        ordered: list[
            KnowledgeConcept
        ] = []

        queue = [
            concept_id
        ]

        while queue:
            current_id = queue.pop(
                0
            )

            for dependent in (
                self.direct_dependents_of(
                    current_id
                )
            ):
                if (
                    dependent.concept_id
                    in visited
                ):
                    continue

                visited.add(
                    dependent.concept_id
                )

                ordered.append(
                    dependent
                )

                queue.append(
                    dependent.concept_id
                )

        return ordered
