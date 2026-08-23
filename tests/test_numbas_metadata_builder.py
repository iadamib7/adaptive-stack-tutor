from pathlib import Path

from backend.app.content.ingestion.numbas.catalog import (
    NumbasCatalog,
)
from backend.app.content.ingestion.numbas.metadata_builder import (
    NumbasMetadataBuilder,
)


SOURCE = Path(
    "resources/raw/numbas/"
    "question-24060-addition-and-"
    "subtraction-of-fractions.exam"
)

CATALOG = Path(
    "resources/raw/numbas/"
    "catalog.json"
)


def test_metadata_is_built_from_real_source() -> None:
    catalog = NumbasCatalog.load(
        CATALOG
    )

    entry = catalog.require(
        "24060"
    )

    metadata = (
        NumbasMetadataBuilder()
        .build(
            path=SOURCE,
            catalog_entry=entry,
        )
    )

    assert metadata.question_id == (
        "24060"
    )

    assert metadata.license_code == (
        "CC-BY-4.0"
    )

    assert (
        "fractions"
        in {
            tag.lower()
            for tag in metadata.tags
        }
    )

    assert (
        "Christian Lawson-Perfect"
        in metadata.author_names
    )
