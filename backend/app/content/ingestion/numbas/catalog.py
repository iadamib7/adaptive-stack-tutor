from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from backend.app.content.ingestion.numbas.models import (
    NumbasQuestionStatus,
)


@dataclass(frozen=True)
class NumbasCatalogEntry:
    question_id: str
    source_url: str
    project_name: str

    status: NumbasQuestionStatus = (
        NumbasQuestionStatus.UNKNOWN
    )

    notes: str = ""

    def __post_init__(self) -> None:
        if not self.question_id.strip():
            raise ValueError(
                "question_id must not be empty."
            )

        if not self.source_url.strip():
            raise ValueError(
                "source_url must not be empty."
            )

        if not self.project_name.strip():
            raise ValueError(
                "project_name must not be empty."
            )


class NumbasCatalog:
    def __init__(
        self,
        entries: list[
            NumbasCatalogEntry
        ],
    ) -> None:
        self._entries: dict[
            str,
            NumbasCatalogEntry,
        ] = {}

        for entry in entries:
            if (
                entry.question_id
                in self._entries
            ):
                raise ValueError(
                    "Duplicate Numbas catalogue "
                    "question ID: "
                    f"{entry.question_id}"
                )

            self._entries[
                entry.question_id
            ] = entry

    def get(
        self,
        question_id: str,
    ) -> NumbasCatalogEntry | None:
        return self._entries.get(
            question_id
        )

    def require(
        self,
        question_id: str,
    ) -> NumbasCatalogEntry:
        entry = self.get(
            question_id
        )

        if entry is None:
            raise ValueError(
                "Unknown Numbas catalogue "
                f"question: {question_id}"
            )

        return entry

    @classmethod
    def load(
        cls,
        path: Path,
    ) -> "NumbasCatalog":
        data = json.loads(
            path.read_text(
                encoding="utf-8-sig"
            )
        )

        raw_entries = data.get(
            "questions",
            []
        )

        entries = [
            NumbasCatalogEntry(
                question_id=str(
                    item["question_id"]
                ),
                source_url=(
                    item["source_url"]
                ),
                project_name=(
                    item["project_name"]
                ),
                status=(
                    NumbasQuestionStatus(
                        item.get(
                            "status",
                            "unknown",
                        )
                    )
                ),
                notes=item.get(
                    "notes",
                    "",
                ),
            )
            for item in raw_entries
        ]

        return cls(
            entries
        )
