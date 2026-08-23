from fractions import Fraction

from backend.app.learning.answer_normalization.numeric import (
    canonicalize_numeric_answer,
    normalize_numeric_answer,
    numerically_equivalent,
)


def test_decimal_and_fraction_are_equivalent() -> None:
    assert numerically_equivalent(
        "3.75",
        "15/4",
    )


def test_half_decimal_and_fraction_are_equivalent() -> None:
    assert numerically_equivalent(
        "0.5",
        "1/2",
    )


def test_integer_and_fraction_are_equivalent() -> None:
    assert numerically_equivalent(
        "2",
        "4/2",
    )


def test_non_equivalent_answers_are_rejected() -> None:
    assert not numerically_equivalent(
        "540",
        "15/4",
    )


def test_rounded_decimal_is_not_exact_third() -> None:
    assert not numerically_equivalent(
        "0.333",
        "1/3",
    )


def test_fraction_is_reduced_to_canonical_form() -> None:
    assert canonicalize_numeric_answer(
        "30/8"
    ) == "15/4"


def test_decimal_is_canonicalized_to_fraction() -> None:
    assert canonicalize_numeric_answer(
        "3.75"
    ) == "15/4"


def test_integer_remains_integer() -> None:
    assert canonicalize_numeric_answer(
        "5"
    ) == "5"


def test_invalid_expression_is_not_numeric() -> None:
    assert normalize_numeric_answer(
        "x + 1"
    ) is None


def test_empty_answer_is_not_numeric() -> None:
    assert normalize_numeric_answer(
        ""
    ) is None


def test_terminating_fraction_has_exact_decimal() -> None:
    result = normalize_numeric_answer(
        "15/4"
    )

    assert result is not None

    assert result.exact_decimal == "3.75"


def test_nonterminating_fraction_has_no_exact_decimal() -> None:
    result = normalize_numeric_answer(
        "1/3"
    )

    assert result is not None

    assert result.fraction == Fraction(
        1,
        3,
    )

    assert result.exact_decimal is None
