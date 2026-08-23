from pathlib import Path

from backend.app.content.ingestion.numbas.importer import (
    NumbasContentImporter,
)


SOURCE = Path(
    "resources/raw/numbas/"
    "question-24060-addition-and-"
    "subtraction-of-fractions.exam"
)


def test_real_numbas_question_imports() -> None:
    record = (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )

    assert record.external_id == (
        "24060"
    )

    assert record.source_provider == (
        "numbas"
    )


def test_real_numbas_import_preserves_title() -> None:
    record = (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )

    assert record.title == (
        "Addition and subtraction "
        "of fractions"
    )


def test_real_numbas_import_has_fraction_context() -> None:
    record = (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )

    assert (
        "fractions"
        in record.category_path.lower()
    )


def test_real_numbas_import_has_six_inputs() -> None:
    record = (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )

    assert len(
        record.input_names
    ) == 6


def test_real_numbas_import_preserves_solution() -> None:
    record = (
        NumbasContentImporter()
        .import_file(
            SOURCE
        )
    )

    assert (
        "common denominator"
        in record.worked_solution.lower()
    )
