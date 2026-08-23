from pathlib import Path

from backend.app.content.ingestion.numbas.parser import (
    NumbasExamParser,
)


SOURCE = Path(
    "resources/raw/numbas/"
    "question-24060-addition-and-"
    "subtraction-of-fractions.exam"
)


def test_real_numbas_question_parses() -> None:
    question = (
        NumbasExamParser()
        .parse(SOURCE)
    )

    assert question.name == (
        "Addition and subtraction "
        "of fractions"
    )

    assert "Evaluate" in (
        question.statement
    )

    assert len(
        question.variables
    ) > 0

    assert len(
        question.parts
    ) == 3


def test_real_numbas_question_has_fraction_tags() -> None:
    question = (
        NumbasExamParser()
        .parse(SOURCE)
    )

    normalised = {
        tag.lower()
        for tag in question.tags
    }

    assert "fractions" in normalised


def test_real_numbas_question_has_cc_by_license() -> None:
    question = (
        NumbasExamParser()
        .parse(SOURCE)
    )

    assert question.licence == (
        "Creative Commons Attribution "
        "4.0 International"
    )


def test_real_numbas_question_preserves_advice() -> None:
    question = (
        NumbasExamParser()
        .parse(SOURCE)
    )

    assert (
        "common denominator"
        in question.advice.lower()
    )


def test_real_numbas_question_preserves_contributors() -> None:
    question = (
        NumbasExamParser()
        .parse(SOURCE)
    )

    assert (
        "Christian Lawson-Perfect"
        in question.contributors
    )

    assert (
        "Lauren Richards"
        in question.contributors
    )


def test_real_numbas_question_is_randomised() -> None:
    question = (
        NumbasExamParser()
        .parse(SOURCE)
    )

    definitions = [
        variable.get(
            "definition",
            "",
        )
        for variable
        in question.variables.values()
    ]

    assert any(
        "random(" in definition
        for definition in definitions
    )


def test_real_numbas_question_has_gapfill_parts() -> None:
    question = (
        NumbasExamParser()
        .parse(SOURCE)
    )

    assert all(
        part.get("type")
        == "gapfill"
        for part in question.parts
    )

    assert all(
        len(
            part.get(
                "gaps",
                [],
            )
        ) == 2
        for part in question.parts
    )
