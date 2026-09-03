import pytest

from backend.app.learning.adaptive_engine import (
    CurriculumIndependentAdaptiveEngine,
    StackXmlQuestionBankImporter,
)


SAMPLE_XML = """
<quiz>
  <question type="category">
    <category>
      <text>Example category</text>
    </category>
  </question>

  <question type="stack">
    <name>
      <text>Diagnostic question</text>
    </name>
    <idnumber>Q1</idnumber>
    <questiontext format="html">
      <text>Question one</text>
    </questiontext>
    <input name="ans1" />
    <prt name="prt1" />
  </question>

  <question type="stack">
    <name>
      <text>Second question</text>
    </name>
    <questiontext format="html">
      <text>Question two</text>
    </questiontext>
    <input name="ans1" />
    <prt name="prt1" />
  </question>
</quiz>
"""


def test_imports_only_stack_questions() -> None:
    importer = (
        StackXmlQuestionBankImporter()
    )

    bank = importer.import_text(
        SAMPLE_XML
    )

    assert bank.count == 2


def test_preserves_explicit_question_id() -> None:
    importer = (
        StackXmlQuestionBankImporter()
    )

    bank = importer.import_text(
        SAMPLE_XML
    )

    item = bank.require(
        "Q1"
    )

    assert (
        item.adaptive_question.title
        == "Diagnostic question"
    )


def test_generates_stable_id_when_missing() -> None:
    importer = (
        StackXmlQuestionBankImporter()
    )

    bank_a = importer.import_text(
        SAMPLE_XML
    )

    bank_b = importer.import_text(
        SAMPLE_XML
    )

    ids_a = [
        question.question_id
        for question
        in bank_a.adaptive_questions()
    ]

    ids_b = [
        question.question_id
        for question
        in bank_b.adaptive_questions()
    ]

    assert ids_a == ids_b


def test_preserves_stack_xml() -> None:
    importer = (
        StackXmlQuestionBankImporter()
    )

    bank = importer.import_text(
        SAMPLE_XML
    )

    item = bank.require(
        "Q1"
    )

    assert "<quiz>" in (
        item.stack_xml
    )

    assert (
        'type="stack"'
        in item.stack_xml
    )


def test_imported_bank_runs_without_curriculum() -> None:
    importer = (
        StackXmlQuestionBankImporter()
    )

    bank = importer.import_text(
        SAMPLE_XML
    )

    engine = (
        CurriculumIndependentAdaptiveEngine(
            bank.adaptive_questions()
        )
    )

    decision = engine.start(
        learner_id=1
    )

    assert decision is not None


def test_invalid_root_rejected() -> None:
    importer = (
        StackXmlQuestionBankImporter()
    )

    with pytest.raises(
        ValueError,
    ):
        importer.import_text(
            "<questions />"
        )


def test_bank_without_stack_questions_rejected() -> None:
    importer = (
        StackXmlQuestionBankImporter()
    )

    with pytest.raises(
        ValueError,
    ):
        importer.import_text(
            """
            <quiz>
              <question type="category">
                <category>
                  <text>Only category</text>
                </category>
              </question>
            </quiz>
            """
        )
