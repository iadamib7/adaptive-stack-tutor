from backend.app.learning.question_quality.mathematical_validator import (
    MathematicalQuestionValidator,
)
from backend.app.learning.question_quality.models import (
    QualityStatus,
)


class FakeResponse:
    def __init__(
        self,
        payload: dict,
        ok: bool = True,
    ) -> None:
        self.payload = payload
        self.ok = ok

    def json(self) -> dict:
        return self.payload


class FakeSession:
    def __init__(
        self,
        scores: dict[str, float | None],
    ) -> None:
        self.scores = scores
        self.answers_seen: list[str] = []

    def post(
        self,
        url: str,
        json: dict,
        timeout: int,
    ) -> FakeResponse:
        answer = json["answers"]["ans1"]

        self.answers_seen.append(
            answer
        )

        score = self.scores.get(
            answer
        )

        return FakeResponse(
            {
                "score": score,
            }
        )


def test_fraction_converts_to_exact_decimal() -> None:
    decimal_answer = (
        MathematicalQuestionValidator
        ._exact_decimal_equivalent(
            "15/4"
        )
    )

    assert decimal_answer == "3.75"


def test_non_terminating_fraction_is_skipped() -> None:
    decimal_answer = (
        MathematicalQuestionValidator
        ._exact_decimal_equivalent(
            "1/3"
        )
    )

    assert decimal_answer is None


def test_equivalent_decimal_passes() -> None:
    session = FakeSession(
        {
            "15/4": 1.0,
            "3.75": 1.0,
        }
    )

    validator = MathematicalQuestionValidator(
        session=session
    )

    check = (
        validator
        .validate_fraction_decimal_equivalence(
            question_xml="<quiz></quiz>",
            seed=123,
            input_name="ans1",
            model_answer="15/4",
        )
    )

    assert check.status == (
        QualityStatus.PASS
    )

    assert session.answers_seen == [
        "15/4",
        "3.75",
    ]


def test_rejected_equivalent_decimal_requires_review() -> None:
    session = FakeSession(
        {
            "15/4": 1.0,
            "3.75": None,
        }
    )

    validator = MathematicalQuestionValidator(
        session=session
    )

    check = (
        validator
        .validate_fraction_decimal_equivalence(
            question_xml="<quiz></quiz>",
            seed=123,
            input_name="ans1",
            model_answer="15/4",
        )
    )

    assert check.status == (
        QualityStatus.REVIEW
    )

    assert "3.75" in check.message


def test_different_scores_require_review() -> None:
    session = FakeSession(
        {
            "15/4": 1.0,
            "3.75": 0.0,
        }
    )

    validator = MathematicalQuestionValidator(
        session=session
    )

    check = (
        validator
        .validate_fraction_decimal_equivalence(
            question_xml="<quiz></quiz>",
            seed=123,
            input_name="ans1",
            model_answer="15/4",
        )
    )

    assert check.status == (
        QualityStatus.REVIEW
    )


def test_model_answer_failure_is_fail() -> None:
    session = FakeSession(
        {
            "15/4": None,
        }
    )

    validator = MathematicalQuestionValidator(
        session=session
    )

    check = (
        validator
        .validate_fraction_decimal_equivalence(
            question_xml="<quiz></quiz>",
            seed=123,
            input_name="ans1",
            model_answer="15/4",
        )
    )

    assert check.status == (
        QualityStatus.FAIL
    )
