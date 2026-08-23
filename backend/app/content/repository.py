from __future__ import annotations

from collections.abc import Iterable

from backend.app.content.models import (
    ContentDifficulty,
    ContentKind,
    LearningContentItem,
)


class LearningContentRepository:
    """
    Provider-independent repository of learning content.
    """

    def __init__(
        self,
        items: Iterable[
            LearningContentItem
        ],
    ) -> None:
        self._items: dict[
            str,
            LearningContentItem,
        ] = {}

        for item in items:
            if (
                item.content_id
                in self._items
            ):
                raise ValueError(
                    "Duplicate content ID: "
                    f"{item.content_id}"
                )

            self._items[
                item.content_id
            ] = item

    def get(
        self,
        content_id: str,
    ) -> LearningContentItem | None:
        return self._items.get(
            content_id
        )

    def require(
        self,
        content_id: str,
    ) -> LearningContentItem:
        item = self.get(
            content_id
        )

        if item is None:
            raise ValueError(
                "Unknown learning content: "
                f"{content_id}"
            )

        return item

    def all_items(
        self,
    ) -> list[LearningContentItem]:
        return list(
            self._items.values()
        )

    def for_concept(
        self,
        concept_id: str,
        *,
        deliverable_only: bool = True,
    ) -> list[LearningContentItem]:
        items = [
            item
            for item in self._items.values()
            if item.concept_id
            == concept_id
        ]

        if deliverable_only:
            items = [
                item
                for item in items
                if item.can_be_delivered
            ]

        return items

    def questions_for_concept(
        self,
        concept_id: str,
        *,
        difficulty: (
            ContentDifficulty
            | None
        ) = None,
        deliverable_only: bool = True,
    ) -> list[LearningContentItem]:
        items = [
            item
            for item in self.for_concept(
                concept_id,
                deliverable_only=(
                    deliverable_only
                ),
            )
            if item.kind
            == ContentKind.QUESTION
        ]

        if difficulty is not None:
            items = [
                item
                for item in items
                if item.difficulty
                == difficulty
            ]

        return items

    def mastery_items_for(
        self,
        concept_id: str,
    ) -> list[LearningContentItem]:
        return [
            item
            for item in self.questions_for_concept(
                concept_id
            )
            if item.is_mastery_evidence
        ]

    def hints_for(
        self,
        concept_id: str,
    ) -> list[LearningContentItem]:
        return [
            item
            for item in self.for_concept(
                concept_id
            )
            if item.kind
            == ContentKind.HINT
        ]

    def excluding_seen(
        self,
        items: Iterable[
            LearningContentItem
        ],
        seen_content_ids: set[str],
    ) -> list[LearningContentItem]:
        return [
            item
            for item in items
            if item.content_id
            not in seen_content_ids
        ]

    def variants_of(
        self,
        content_id: str,
    ) -> list[LearningContentItem]:
        item = self.require(
            content_id
        )

        if item.variant_group_id is None:
            return []

        return [
            candidate
            for candidate
            in self._items.values()
            if candidate.content_id
            != item.content_id
            and candidate.variant_group_id
            == item.variant_group_id
            and candidate.can_be_delivered
        ]
