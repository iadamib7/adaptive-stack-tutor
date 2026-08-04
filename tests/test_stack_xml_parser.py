from pathlib import Path

import pytest

from backend.app.integrations.stack_xml.parser import (
    StackXMLParser,
)


FIXTURE = Path(
    "tests/fixtures/stack_xml/Question_1.xml"
)


def test_parser_reads_question_name() -> None:
    question = StackXMLParser().parse_file(FIXTURE)

    assert (
        question.question_name
        == "Integration Method Decision"
    )
    assert question.filename == "Question_1.xml"


def test_parser_reads_single_prt() -> None:
    question = StackXMLParser().parse_file(FIXTURE)

    assert len(question.prts) == 1
    assert question.prts[0].name == "prt1"


def test_parser_reads_prt_nodes() -> None:
    question = StackXMLParser().parse_file(FIXTURE)

    nodes = question.prts[0].nodes

    assert len(nodes) == 2
    assert nodes[0].number == 1
    assert nodes[1].number == 2


def test_parser_distinguishes_internal_and_exit_branches() -> None:
    question = StackXMLParser().parse_file(FIXTURE)

    first_node = question.prts[0].nodes[0]

    assert first_node.true_branch.exits_tree is True
    assert first_node.false_branch.next_node == 2
    assert first_node.false_branch.exits_tree is False


def test_missing_file_raises_clear_error() -> None:
    with pytest.raises(
        FileNotFoundError,
        match="STACK XML file was not found",
    ):
        StackXMLParser().parse_file(
            Path("missing.xml")
        )
