from __future__ import annotations

from collections.abc import Iterable

from backend.app.content.sources.models import (
    ContentSourceDefinition,
)


class ContentSourceRegistry:
    def __init__(
        self,
        sources: Iterable[
            ContentSourceDefinition
        ],
    ) -> None:
        self._sources: dict[
            str,
            ContentSourceDefinition,
        ] = {}

        for source in sources:
            if source.source_id in self._sources:
                raise ValueError(
                    "Duplicate content source ID: "
                    f"{source.source_id}"
                )

            self._sources[
                source.source_id
            ] = source

    def get(
        self,
        source_id: str,
    ) -> ContentSourceDefinition | None:
        return self._sources.get(
            source_id
        )

    def require(
        self,
        source_id: str,
    ) -> ContentSourceDefinition:
        source = self.get(
            source_id
        )

        if source is None:
            raise ValueError(
                "Unknown content source: "
                f"{source_id}"
            )

        return source

    def all_sources(
        self,
    ) -> list[
        ContentSourceDefinition
    ]:
        return list(
            self._sources.values()
        )
