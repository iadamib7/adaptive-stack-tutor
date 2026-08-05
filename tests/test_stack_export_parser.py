from pathlib import Path

from backend.app.integrations.stack_xml.export_parser import (
    StackExportParser,
)


FIXTURE = Path(
    "tests/fixtures/stack_xml/grade9_export.xml"
)


def parse_inventory():
    return StackExportParser().parse(
        path=FIXTURE,
        profile_id="kenya-grade9-development",
    )


def test_parses_multiple_stack_questions() -> None:
    inventory = parse_inventory()

    assert inventory.question_count == 2


def test_preserves_question_identifier() -> None:
    inventory = parse_inventory()

    assert (
        inventory.questions[0].source_question_id
        == "207582"
    )


def test_preserves_curriculum_category_path() -> None:
    inventory = parse_inventory()

    assert inventory.questions[0].category_path == [
        "Grade 9",
        "1.0 Whole Numbers",
        "1.1 Integers",
    ]


def test_extracts_inputs_and_prts() -> None:
    question = parse_inventory().questions[0]

    assert question.input_names == ["ans1"]
    assert question.prt_names == ["prt1"]
    assert question.prt_count == 1
    assert question.node_count == 1


def test_simple_question_is_identified() -> None:
    question = parse_inventory().questions[0]

    assert question.simple_single_prt is True


def test_complex_question_is_not_simple() -> None:
    question = parse_inventory().questions[1]

    assert question.simple_single_prt is False
    assert question.node_count == 2


def test_answer_notes_are_canonical_outcomes() -> None:
    question = parse_inventory().questions[1]

    outcome_codes = {
        outcome.outcome_code
        for outcome in question.outcomes
    }

    assert outcome_codes == {
        "prt1-1-T",
        "prt1-1-F",
        "prt1-2-T",
        "prt1-2-F",
    }


def test_internal_and_exit_branches_are_distinguished() -> None:
    question = parse_inventory().questions[1]

    internal_branch = next(
        outcome
        for outcome in question.outcomes
        if outcome.outcome_code == "prt1-1-F"
    )

    rounding_branch = next(
        outcome
        for outcome in question.outcomes
        if outcome.outcome_code == "prt1-2-T"
    )

    assert internal_branch.next_node == "1"
    assert internal_branch.exits_tree is False

    assert rounding_branch.next_node is None
    assert rounding_branch.exits_tree is True
    assert rounding_branch.score == 0.25
    assert "rounding" in (
        rounding_branch.feedback or ""
    ).casefold()
