from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any

import requests

from backend.app.learning.question_quality.models import (
    QualityCheck,
    QualityStatus,
)


class MathematicalQuestionValidator:
    """
    Check mathematical answer consistency for STACK questions.

    The first implemented check verifies that an exact
    fraction model answer and its equivalent terminating
    decimal receive the same grading result.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3080",
        timeout_seconds: int = 120,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

        self.session = (
            session
            if session is not None
            else requests.Session()
        )

    def validate_fraction_decimal_equivalence(
        self,
        question_xml: str,
        seed: int,
        input_name: str,
        model_answer: str,
    ) -> QualityCheck:
        decimal_answer = (
            self._exact_decimal_equivalent(
                model_answer
            )
        )

        if decimal_answer is None:
            return QualityCheck(
                name="Mathematical equivalence",
                status=QualityStatus.PASS,
                message=(
                    "No distinct terminating decimal "
                    "equivalent requires checking."
                ),
            )

        model_score = self._grade_answer(
            question_xml=question_xml,
            seed=seed,
            input_name=input_name,
            answer=model_answer,
        )

        if model_score is None:
            return QualityCheck(
                name="Mathematical equivalence",
                status=QualityStatus.FAIL,
                message=(
                    f"The model answer {model_answer} "
                    "could not be graded successfully."
                ),
            )

        decimal_score = self._grade_answer(
            question_xml=question_xml,
            seed=seed,
            input_name=input_name,
            answer=decimal_answer,
        )

        if decimal_score is None:
            return QualityCheck(
                name="Mathematical equivalence",
                status=QualityStatus.REVIEW,
                message=(
                    f"The model answer {model_answer} "
                    f"is accepted, but its mathematically "
                    f"equivalent decimal {decimal_answer} "
                    "is not accepted."
                ),
            )

        if decimal_score != model_score:
            return QualityCheck(
                name="Mathematical equivalence",
                status=QualityStatus.REVIEW,
                message=(
                    f"The equivalent answers "
                    f"{model_answer} and {decimal_answer} "
                    "receive different STACK scores."
                ),
            )

        return QualityCheck(
            name="Mathematical equivalence",
            status=QualityStatus.PASS,
            message=(
                f"Equivalent answers {model_answer} "
                f"and {decimal_answer} receive the "
                "same STACK score."
            ),
        )

    def _grade_answer(
        self,
        question_xml: str,
        seed: int,
        input_name: str,
        answer: str,
    ) -> float | None:
        try:
            response = self.session.post(
                f"{self.base_url}/grade",
                json={
                    "questionDefinition":
                        question_xml,
                    "seed": seed,
                    "answers": {
                        input_name: answer,
                    },
                },
                timeout=self.timeout_seconds,
            )
        except requests.RequestException:
            return None

        if not response.ok:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        if not isinstance(payload, dict):
            return None

        score = payload.get("score")

        if not isinstance(
            score,
            (int, float),
        ):
            return None

        return float(score)

    @staticmethod
    def _exact_decimal_equivalent(
        answer: str,
    ) -> str | None:
        try:
            fraction = Fraction(
                answer.strip()
            )
        except (
            ValueError,
            ZeroDivisionError,
        ):
            return None

        denominator = (
            fraction.denominator
        )

        remaining = denominator

        while remaining % 2 == 0:
            remaining //= 2

        while remaining % 5 == 0:
            remaining //= 5

        if remaining != 1:
            return None

        decimal_value = (
            Decimal(fraction.numerator)
            / Decimal(fraction.denominator)
        )

        decimal_text = format(
            decimal_value,
            "f",
        )

        if "." in decimal_text:
            decimal_text = (
                decimal_text.rstrip("0")
                .rstrip(".")
            )

        normalized_original = (
            answer.strip()
        )

        if decimal_text == normalized_original:
            return None

        return decimal_text
