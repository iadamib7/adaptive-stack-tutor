from pathlib import Path

from backend.app.content.ingestion.stack_importer import (
    StackContentImporter,
)


REAL_EXPORT = Path(
    "resources/raw/kenya/grade9/"
    "grade9_questions.xml"
)


def test_real_grade9_export_imports_questions() -> None:
    records = (
        StackContentImporter()
        .import_file(
            REAL_EXPORT
        )
    )

    assert len(records) >= 70


def test_real_integer_question_is_imported() -> None:
    records = (
        StackContentImporter()
        .import_file(
            REAL_EXPORT
        )
    )

    by_id = {
        record.external_id: record
        for record in records
    }

    assert "207582" in by_id

    assert (
        "integer"
        in by_id[
            "207582"
        ].category_path.lower()
    )


def test_real_indices_question_has_multiple_inputs() -> None:
    records = (
        StackContentImporter()
        .import_file(
            REAL_EXPORT
        )
    )

    by_id = {
        record.external_id: record
        for record in records
    }

    question = by_id[
        "206946"
    ]

    assert len(
        question.input_names
    ) == 8

    assert len(
        question.prt_names
    ) == 8
