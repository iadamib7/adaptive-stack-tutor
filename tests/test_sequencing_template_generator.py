from pathlib import Path

from backend.app.integrations.stack_xml.parser import (
    StackXMLParser,
)
from backend.app.integrations.stack_xml.template_generator import (
    SequencingTemplateGenerator,
)


FIXTURE = Path(
    "tests/fixtures/stack_xml/Question_1.xml"
)


def test_generator_creates_question_entry() -> None:
    question = StackXMLParser().parse_file(FIXTURE)

    entry = (
        SequencingTemplateGenerator()
        .generate_question_entry(question)
    )

    assert "Question_1.xml" in entry


def test_generator_includes_only_prt_exit_branches() -> None:
    question = StackXMLParser().parse_file(FIXTURE)

    entry = (
        SequencingTemplateGenerator()
        .generate_question_entry(question)
    )

    outcomes = entry[
        "Question_1.xml"
    ]["prts"]["prt1"]["outcomes"]

    assert set(outcomes) == {
        "prt-1-T",
        "prt-2-T",
        "prt-2-F",
    }


def test_generated_routes_are_blank_teacher_templates() -> None:
    question = StackXMLParser().parse_file(FIXTURE)

    entry = (
        SequencingTemplateGenerator()
        .generate_question_entry(question)
    )

    route = entry[
        "Question_1.xml"
    ]["prts"]["prt1"]["outcomes"]["prt-1-T"]

    assert route["strategy"] == "fixed"
    assert route["next_questions"] == []
    assert route["allow_loop"] is False
    assert "TODO" in route["reason"]
