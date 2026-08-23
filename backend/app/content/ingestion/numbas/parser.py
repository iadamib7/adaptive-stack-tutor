from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class NumbasParseError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedNumbasQuestion:
    name: str
    statement: str
    variables: dict[str, Any]
    tags: tuple[str, ...]
    parts: tuple[dict[str, Any], ...]
    advice: str
    description: str
    licence: str
    contributors: tuple[str, ...]
    raw_question: dict[str, Any]


class NumbasExamParser:
    def parse(
        self,
        path: Path,
    ) -> ParsedNumbasQuestion:
        if not path.exists():
            raise NumbasParseError(
                f"Numbas source does not exist: {path}"
            )

        text = path.read_text(
            encoding="utf-8-sig"
        )

        payload = self._load_payload(text)

        groups = payload.get(
            "question_groups",
            [],
        )

        if not groups:
            raise NumbasParseError(
                "Numbas source contains no "
                "question groups."
            )

        questions = groups[0].get(
            "questions",
            [],
        )

        if not questions:
            raise NumbasParseError(
                "Numbas source contains no "
                "questions."
            )

        question = questions[0]

        metadata = question.get(
            "metadata",
            {},
        )

        contributors = question.get(
            "contributors",
            payload.get(
                "contributors",
                [],
            ),
        )

        contributor_names = tuple(
            item.get(
                "name",
                "",
            ).strip()
            for item in contributors
            if item.get(
                "name",
                "",
            ).strip()
        )

        return ParsedNumbasQuestion(
            name=question.get(
                "name",
                "",
            ).strip(),
            statement=question.get(
                "statement",
                "",
            ),
            variables=dict(
                question.get(
                    "variables",
                    {},
                )
            ),
            tags=tuple(
                question.get(
                    "tags",
                    [],
                )
            ),
            parts=tuple(
                question.get(
                    "parts",
                    [],
                )
            ),
            advice=question.get(
                "advice",
                "",
            ),
            description=metadata.get(
                "description",
                "",
            ),
            licence=metadata.get(
                "licence",
                "",
            ).strip(),
            contributors=(
                contributor_names
            ),
            raw_question=question,
        )

    @staticmethod
    def _load_payload(
        text: str,
    ) -> dict[str, Any]:
        lines = text.splitlines()

        while (
            lines
            and not lines[0].strip()
        ):
            lines.pop(0)

        if (
            lines
            and lines[0]
            .lstrip()
            .startswith("//")
        ):
            lines = lines[1:]

        json_text = "\n".join(
            lines
        ).strip()

        if not json_text:
            raise NumbasParseError(
                "Numbas source is empty."
            )

        try:
            payload = json.loads(
                json_text
            )
        except json.JSONDecodeError as error:
            raise NumbasParseError(
                "Numbas source does not contain "
                "valid JSON."
            ) from error

        if not isinstance(
            payload,
            dict,
        ):
            raise NumbasParseError(
                "Numbas source root must be "
                "a JSON object."
            )

        return payload
