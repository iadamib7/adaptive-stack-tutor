from pathlib import Path

from backend.app.content.ingestion.stack_importer import (
    StackContentImporter,
)


def write_export(
    tmp_path: Path,
) -> Path:
    path = tmp_path / "questions.xml"

    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<quiz>

<!-- question: 0 -->
<question type="category">
    <category>
        <text>
            $course$/top/Grade 9/Number/Fractions
        </text>
    </category>
</question>

<!-- question: 1001 -->
<question type="stack">
    <name>
        <text>Add fractions</text>
    </name>

    <questiontext>
        <text><![CDATA[
            <p>Add the fractions.</p>
            [[input:ans1]]
            [[feedback:prt1]]
        ]]></text>
    </questiontext>

    <generalfeedback>
        <text><![CDATA[
            <p>Worked solution</p>
        ]]></text>
    </generalfeedback>

    <questionnote>
        <text>fraction addition</text>
    </questionnote>

    <input>
        <name>ans1</name>
    </input>

    <prt>
        <name>prt1</name>
    </prt>

    <deployedseed>123</deployedseed>
    <deployedseed>456</deployedseed>
</question>

<!-- question: 0 -->
<question type="category">
    <category>
        <text>
            $course$/top/Grade 9/Algebra
        </text>
    </category>
</question>

<!-- question: 1002 -->
<question type="stack">
    <name>
        <text>Simplify algebra</text>
    </name>

    <questiontext>
        <text>
            Simplify [[input:ans1]]
        </text>
    </questiontext>

    <input>
        <name>ans1</name>
    </input>

    <prt>
        <name>prt1</name>
    </prt>
</question>

</quiz>
""",
        encoding="utf-8",
    )

    return path


def test_imports_stack_questions(
    tmp_path: Path,
) -> None:
    records = (
        StackContentImporter()
        .import_file(
            write_export(
                tmp_path
            )
        )
    )

    assert len(records) == 2


def test_preserves_source_question_id(
    tmp_path: Path,
) -> None:
    records = (
        StackContentImporter()
        .import_file(
            write_export(
                tmp_path
            )
        )
    )

    assert records[0].external_id == (
        "1001"
    )


def test_preserves_category_context(
    tmp_path: Path,
) -> None:
    records = (
        StackContentImporter()
        .import_file(
            write_export(
                tmp_path
            )
        )
    )

    assert (
        "Fractions"
        in records[0].category_path
    )

    assert (
        "Algebra"
        in records[1].category_path
    )


def test_extracts_inputs_and_prts(
    tmp_path: Path,
) -> None:
    record = (
        StackContentImporter()
        .import_file(
            write_export(
                tmp_path
            )
        )[0]
    )

    assert record.input_names == (
        "ans1",
    )

    assert record.prt_names == (
        "prt1",
    )


def test_extracts_worked_solution(
    tmp_path: Path,
) -> None:
    record = (
        StackContentImporter()
        .import_file(
            write_export(
                tmp_path
            )
        )[0]
    )

    assert "Worked solution" in (
        record.worked_solution
    )


def test_extracts_deployed_seeds(
    tmp_path: Path,
) -> None:
    record = (
        StackContentImporter()
        .import_file(
            write_export(
                tmp_path
            )
        )[0]
    )

    assert record.deployed_seeds == (
        123,
        456,
    )
