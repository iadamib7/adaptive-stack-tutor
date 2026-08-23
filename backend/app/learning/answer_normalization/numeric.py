from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction


@dataclass(frozen=True)
class NormalizedNumericAnswer:
    original: str
    fraction: Fraction

    @property
    def canonical_fraction(self) -> str:
        if self.fraction.denominator == 1:
            return str(
                self.fraction.numerator
            )

        return (
            f"{self.fraction.numerator}/"
            f"{self.fraction.denominator}"
        )

    @property
    def exact_decimal(self) -> str | None:
        denominator = (
            self.fraction.denominator
        )

        remaining = denominator

        while remaining % 2 == 0:
            remaining //= 2

        while remaining % 5 == 0:
            remaining //= 5

        if remaining != 1:
            return None

        value = (
            Decimal(self.fraction.numerator)
            / Decimal(self.fraction.denominator)
        )

        text = format(
            value,
            "f",
        )

        if "." in text:
            text = (
                text.rstrip("0")
                .rstrip(".")
            )

        return text


def normalize_numeric_answer(
    answer: str,
) -> NormalizedNumericAnswer | None:
    value = answer.strip()

    if not value:
        return None

    fraction = _parse_fraction(
        value
    )

    if fraction is None:
        fraction = _parse_decimal(
            value
        )

    if fraction is None:
        return None

    return NormalizedNumericAnswer(
        original=value,
        fraction=fraction,
    )


def numerically_equivalent(
    left: str,
    right: str,
) -> bool:
    normalized_left = (
        normalize_numeric_answer(
            left
        )
    )

    normalized_right = (
        normalize_numeric_answer(
            right
        )
    )

    if (
        normalized_left is None
        or normalized_right is None
    ):
        return False

    return (
        normalized_left.fraction
        == normalized_right.fraction
    )


def canonicalize_numeric_answer(
    answer: str,
) -> str | None:
    normalized = (
        normalize_numeric_answer(
            answer
        )
    )

    if normalized is None:
        return None

    return normalized.canonical_fraction


def _parse_fraction(
    value: str,
) -> Fraction | None:
    if "/" not in value:
        return None

    try:
        return Fraction(value)
    except (
        ValueError,
        ZeroDivisionError,
    ):
        return None


def _parse_decimal(
    value: str,
) -> Fraction | None:
    try:
        decimal_value = Decimal(
            value
        )
    except InvalidOperation:
        return None

    if not decimal_value.is_finite():
        return None

    return Fraction(
        decimal_value
    )
