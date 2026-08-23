from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImportedContentRecord:
    """
    Provider-neutral intermediate representation.

    Source-specific importers create these records.
    Later pipeline stages map them into LearningContentItem
    objects.
    """

    source_provider: str
    source_reference: str
    external_id: str
    title: str

    question_text: str = ""
    worked_solution: str = ""
    question_note: str = ""

    category_path: str = ""

    input_names: tuple[str, ...] = field(
        default_factory=tuple
    )

    prt_names: tuple[str, ...] = field(
        default_factory=tuple
    )

    deployed_seeds: tuple[int, ...] = field(
        default_factory=tuple
    )

    metadata: tuple[
        tuple[str, str],
        ...
    ] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not self.source_provider.strip():
            raise ValueError(
                "source_provider must not be empty."
            )

        if not self.external_id.strip():
            raise ValueError(
                "external_id must not be empty."
            )

        if not self.title.strip():
            raise ValueError(
                "Imported content title must not be empty."
            )
