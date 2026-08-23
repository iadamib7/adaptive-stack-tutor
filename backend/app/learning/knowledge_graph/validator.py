from __future__ import annotations

from dataclasses import dataclass

from backend.app.learning.knowledge_graph.models import (
    KnowledgeConcept,
)


@dataclass(frozen=True)
class KnowledgeGraphValidationError:
    code: str
    message: str
    concept_id: str | None = None


class KnowledgeGraphValidator:
    def validate(
        self,
        concepts: list[
            KnowledgeConcept
        ],
    ) -> list[
        KnowledgeGraphValidationError
    ]:
        errors: list[
            KnowledgeGraphValidationError
        ] = []

        by_id: dict[
            str,
            KnowledgeConcept,
        ] = {}

        for concept in concepts:
            if concept.concept_id in by_id:
                errors.append(
                    KnowledgeGraphValidationError(
                        code=(
                            "duplicate_concept"
                        ),
                        message=(
                            "Duplicate concept ID: "
                            f"{concept.concept_id}"
                        ),
                        concept_id=(
                            concept.concept_id
                        ),
                    )
                )
            else:
                by_id[
                    concept.concept_id
                ] = concept

        errors.extend(
            self._validate_references(
                by_id
            )
        )

        errors.extend(
            self._validate_cycles(
                by_id
            )
        )

        return errors

    def require_valid(
        self,
        concepts: list[
            KnowledgeConcept
        ],
    ) -> None:
        errors = self.validate(
            concepts
        )

        if not errors:
            return

        message = "; ".join(
            error.message
            for error in errors
        )

        raise ValueError(
            "Invalid knowledge graph: "
            + message
        )

    def _validate_references(
        self,
        by_id: dict[
            str,
            KnowledgeConcept,
        ],
    ) -> list[
        KnowledgeGraphValidationError
    ]:
        errors: list[
            KnowledgeGraphValidationError
        ] = []

        known_ids = set(
            by_id
        )

        for concept in (
            by_id.values()
        ):
            references = {
                "prerequisite":
                    concept
                    .prerequisite_concept_ids,

                "remediation":
                    concept
                    .remediation_concept_ids,

                "extension":
                    concept
                    .extension_concept_ids,
            }

            for (
                relation,
                concept_ids,
            ) in references.items():
                for referenced_id in (
                    concept_ids
                ):
                    if (
                        referenced_id
                        in known_ids
                    ):
                        continue

                    errors.append(
                        KnowledgeGraphValidationError(
                            code=(
                                "unknown_reference"
                            ),
                            message=(
                                f"{concept.concept_id} "
                                f"references unknown "
                                f"{relation} concept "
                                f"{referenced_id}."
                            ),
                            concept_id=(
                                concept.concept_id
                            ),
                        )
                    )

        return errors

    def _validate_cycles(
        self,
        by_id: dict[
            str,
            KnowledgeConcept,
        ],
    ) -> list[
        KnowledgeGraphValidationError
    ]:
        errors: list[
            KnowledgeGraphValidationError
        ] = []

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(
            concept_id: str,
            path: list[str],
        ) -> None:
            if concept_id in visited:
                return

            if concept_id in visiting:
                cycle_start = path.index(
                    concept_id
                )

                cycle = (
                    path[cycle_start:]
                    + [concept_id]
                )

                errors.append(
                    KnowledgeGraphValidationError(
                        code=(
                            "prerequisite_cycle"
                        ),
                        message=(
                            "Prerequisite cycle detected: "
                            + " -> ".join(
                                cycle
                            )
                        ),
                        concept_id=concept_id,
                    )
                )

                return

            visiting.add(
                concept_id
            )

            concept = by_id[
                concept_id
            ]

            for prerequisite_id in (
                concept
                .prerequisite_concept_ids
            ):
                if (
                    prerequisite_id
                    not in by_id
                ):
                    continue

                visit(
                    prerequisite_id,
                    path
                    + [concept_id],
                )

            visiting.remove(
                concept_id
            )

            visited.add(
                concept_id
            )

        for concept_id in by_id:
            visit(
                concept_id,
                [],
            )

        return errors
