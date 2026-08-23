from __future__ import annotations

import json
from pathlib import Path

from backend.app.learning.knowledge_graph.models import (
    ConceptDifficultyBand,
    KnowledgeConcept,
)
from backend.app.learning.knowledge_graph.validator import (
    KnowledgeGraphValidator,
)


def load_knowledge_graph(
    path: Path,
) -> list[KnowledgeConcept]:
    data = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    raw_concepts = data.get(
        "concepts"
    )

    if not isinstance(
        raw_concepts,
        list,
    ):
        raise ValueError(
            "Knowledge graph must contain "
            "a concepts list."
        )

    concepts: list[
        KnowledgeConcept
    ] = []

    for item in raw_concepts:
        concepts.append(
            KnowledgeConcept(
                concept_id=item[
                    "concept_id"
                ],
                name=item["name"],
                domain=item["domain"],
                strand=item["strand"],
                level_id=item["level_id"],
                description=item.get(
                    "description",
                    "",
                ),
                difficulty_band=(
                    ConceptDifficultyBand(
                        item.get(
                            "difficulty_band",
                            "developing",
                        )
                    )
                ),
                prerequisite_concept_ids=tuple(
                    item.get(
                        "prerequisites",
                        [],
                    )
                ),
                remediation_concept_ids=tuple(
                    item.get(
                        "remediation",
                        [],
                    )
                ),
                extension_concept_ids=tuple(
                    item.get(
                        "extensions",
                        [],
                    )
                ),
                mastery_threshold=float(
                    item.get(
                        "mastery_threshold",
                        0.8,
                    )
                ),
                recommended_question_count=int(
                    item.get(
                        "recommended_question_count",
                        5,
                    )
                ),
                curriculum_tags=tuple(
                    item.get(
                        "curriculum_tags",
                        [],
                    )
                ),
            )
        )

    KnowledgeGraphValidator().require_valid(
        concepts
    )

    return concepts
