from __future__ import annotations

from collections.abc import Iterable

from backend.app.learning.curriculum_mapping.models import (
    CurriculumConceptAlignment,
)


class CurriculumAlignmentRepository:
    """
    Read-only repository for curriculum-to-knowledge
    concept alignments.

    A shared knowledge concept may be aligned with
    multiple curriculum concepts.
    """

    def __init__(
        self,
        alignments: Iterable[
            CurriculumConceptAlignment
        ],
    ) -> None:
        self._alignments = list(alignments)

        self._by_curriculum_concept: dict[
            tuple[str, str],
            CurriculumConceptAlignment,
        ] = {}

        self._by_knowledge_concept: dict[
            str,
            list[CurriculumConceptAlignment],
        ] = {}

        self._by_content_standard: dict[
            tuple[str, str],
            list[CurriculumConceptAlignment],
        ] = {}

        self._by_learning_indicator: dict[
            tuple[str, str],
            list[CurriculumConceptAlignment],
        ] = {}

        self._build_indexes()

    def _build_indexes(self) -> None:
        for alignment in self._alignments:
            curriculum_key = (
                alignment.curriculum_profile_id,
                alignment.curriculum_concept_id,
            )

            if curriculum_key in (
                self._by_curriculum_concept
            ):
                raise ValueError(
                    "Duplicate curriculum concept "
                    "alignment: "
                    f"{alignment.curriculum_profile_id}/"
                    f"{alignment.curriculum_concept_id}"
                )

            self._by_curriculum_concept[
                curriculum_key
            ] = alignment

            self._by_knowledge_concept.setdefault(
                alignment.knowledge_concept_id,
                [],
            ).append(
                alignment
            )

            for standard_id in (
                alignment.content_standard_ids
            ):
                standard_key = (
                    alignment.curriculum_profile_id,
                    standard_id,
                )

                self._by_content_standard.setdefault(
                    standard_key,
                    [],
                ).append(
                    alignment
                )

            for indicator_id in (
                alignment.learning_indicator_ids
            ):
                indicator_key = (
                    alignment.curriculum_profile_id,
                    indicator_id,
                )

                self._by_learning_indicator.setdefault(
                    indicator_key,
                    [],
                ).append(
                    alignment
                )

    def all_alignments(
        self,
    ) -> list[CurriculumConceptAlignment]:
        return self._alignments.copy()

    def get_for_curriculum_concept(
        self,
        curriculum_profile_id: str,
        curriculum_concept_id: str,
    ) -> CurriculumConceptAlignment | None:
        return self._by_curriculum_concept.get(
            (
                curriculum_profile_id,
                curriculum_concept_id,
            )
        )

    def require_for_curriculum_concept(
        self,
        curriculum_profile_id: str,
        curriculum_concept_id: str,
    ) -> CurriculumConceptAlignment:
        alignment = (
            self.get_for_curriculum_concept(
                curriculum_profile_id,
                curriculum_concept_id,
            )
        )

        if alignment is None:
            raise ValueError(
                "Unknown curriculum concept "
                "alignment: "
                f"{curriculum_profile_id}/"
                f"{curriculum_concept_id}"
            )

        return alignment

    def get_for_knowledge_concept(
        self,
        knowledge_concept_id: str,
    ) -> list[CurriculumConceptAlignment]:
        return self._by_knowledge_concept.get(
            knowledge_concept_id,
            [],
        ).copy()

    def get_for_content_standard(
        self,
        curriculum_profile_id: str,
        content_standard_id: str,
    ) -> list[CurriculumConceptAlignment]:
        return self._by_content_standard.get(
            (
                curriculum_profile_id,
                content_standard_id,
            ),
            [],
        ).copy()

    def get_for_learning_indicator(
        self,
        curriculum_profile_id: str,
        learning_indicator_id: str,
    ) -> list[CurriculumConceptAlignment]:
        return self._by_learning_indicator.get(
            (
                curriculum_profile_id,
                learning_indicator_id,
            ),
            [],
        ).copy()
