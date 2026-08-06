from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from backend.app.integrations.stack_xml.question_extractor import (
    StackQuestionNotFoundError,
    extract_stack_question,
    write_stack_question,
)


EXPORT_XML = """
<quiz>
  <question type="category">
    <category>
      <text>$course$/Grade 9/Integers</text>
    </category>
  </question>

  <question type="stack">
    <name>
      <text>Addition of integers</text>
    </name>
    <idnumber>207582</idnumber>
    <questiontext format="html">
      <text>Calculate 2 + 3.</text>
    </questiontext>
  </question>

  <question type="stack">
    <name>
      <text>Subtraction of integers</text>
    </name>
    <idnumber>207596</idnumber>
    <questiontext format="html">
      <text>Calculate 5 - 2.</text>
    </questiontext>
  </question>
</quiz>
""".strip()


def create_export(tmp_path: Path) -> Path:
    export_path = tmp_path / "questions.xml"

    export_path.write_text(
        EXPORT_XML,
        encoding="utf-8",
    )

    return export_path


def test_extracts_requested_stack_question(
    tmp_path: Path,
) -> None:
    export_path = create_export(tmp_path)

    extracted = extract_stack_question(
        export_path=export_path,
        question_id="207582",
    )

    root = ET.fromstring(extracted)

    questions = root.findall("question")

    assert len(questions) == 1
    assert questions[0].get("type") == "stack"
    assert (
        questions[0].findtext("idnumber")
        == "207582"
    )


def test_does_not_include_other_questions(
    tmp_path: Path,
) -> None:
    export_path = create_export(tmp_path)

    extracted = extract_stack_question(
        export_path=export_path,
        question_id="207582",
    )

    assert "207596" not in extracted
    assert "Subtraction of integers" not in extracted


def test_category_entries_are_not_returned(
    tmp_path: Path,
) -> None:
    export_path = create_export(tmp_path)

    with pytest.raises(
        StackQuestionNotFoundError
    ):
        extract_stack_question(
            export_path=export_path,
            question_id="$course$/Grade 9/Integers",
        )


def test_unknown_question_is_rejected(
    tmp_path: Path,
) -> None:
    export_path = create_export(tmp_path)

    with pytest.raises(
        StackQuestionNotFoundError,
        match="UNKNOWN",
    ):
        extract_stack_question(
            export_path=export_path,
            question_id="UNKNOWN",
        )


def test_writes_extracted_question(
    tmp_path: Path,
) -> None:
    export_path = create_export(tmp_path)
    output_path = tmp_path / "generated" / "207582.xml"

    returned_path = write_stack_question(
        export_path=export_path,
        question_id="207582",
        output_path=output_path,
    )

    assert returned_path == output_path
    assert output_path.is_file()
    assert "207582" in output_path.read_text(
        encoding="utf-8"
    )


def test_missing_export_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError):
        extract_stack_question(
            export_path=tmp_path / "missing.xml",
            question_id="207582",
        )
