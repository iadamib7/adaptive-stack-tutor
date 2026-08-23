from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NumbasQuestionStatus(
    str,
    Enum,
):
    READY = "ready_to_use"
    NEEDS_TESTING = "needs_to_be_tested"
    HAS_PROBLEMS = "has_some_problems"
    SHOULD_NOT_USE = "should_not_be_used"
    DOES_NOT_WORK = "does_not_work"
    DRAFT = "draft"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class NumbasQuestionMetadata:
    question_id: str
    title: str
    source_url: str
    project_name: str

    description: str = ""

    status: NumbasQuestionStatus = (
        NumbasQuestionStatus.UNKNOWN
    )

    license_code: str = ""
    license_url: str = ""

    tags: tuple[str, ...] = field(
        default_factory=tuple
    )

    taxonomy_paths: tuple[str, ...] = field(
        default_factory=tuple
    )

    ability_levels: tuple[str, ...] = field(
        default_factory=tuple
    )

    author_names: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not self.question_id.strip():
            raise ValueError(
                "question_id must not be empty."
            )

        if not self.title.strip():
            raise ValueError(
                "title must not be empty."
            )

        if not self.source_url.strip():
            raise ValueError(
                "source_url must not be empty."
            )

        if not self.project_name.strip():
            raise ValueError(
                "project_name must not be empty."
            )
