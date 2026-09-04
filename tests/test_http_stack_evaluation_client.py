import pytest
import requests

from backend.app.integrations.stack_api.http_client import (
    HttpStackEvaluationClient,
    StackApiConnectionError,
    StackApiResponseError,
)
from backend.app.integrations.stack_api.models import (
    StackEvaluationRequest,
)


class FakeResponse:
    def __init__(
        self,
        payload: object,
        ok: bool = True,
        json_error: bool = False,
    ) -> None:
        self.payload = payload
        self.ok = ok
        self.json_error = json_error

    def json(self) -> object:
        if self.json_error:
            raise ValueError(
                "Invalid JSON"
            )

        return self.payload


class FakeSession:
    def __init__(
        self,
        responses: list[FakeResponse] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.responses = (
            list(responses)
            if responses is not None
            else []
        )

        self.error = error

        self.requests: list[dict] = []

    def post(
        self,
        url: str,
        json: dict,
        timeout: int,
    ) -> FakeResponse:
        self.requests.append(
            {
                "url": url,
                "json": json,
                "timeout": timeout,
            }
        )

        if self.error is not None:
            raise self.error

        assert self.responses

        return self.responses.pop(0)


def build_request(
    answer: str = "32",
) -> StackEvaluationRequest:
    return StackEvaluationRequest(
        question_id="207582",
        question_xml=(
            "<quiz>"
            "<question type='stack'>"
            "</question>"
            "</quiz>"
        ),
        student_answers={
            "ans1": answer,
        },
        seed=683620564,
    )


def correct_payload() -> dict:
    return {
        "isgradable": True,
        "score": 1,
        "specificfeedback": "",
        "prts": {
            "prt1": (
                "<div class='correct'>"
                "Correct answer, well done."
                "</div>"
            ),
        },
        "prtresults": {
            "prt1": {
                "score": 1,
                "penalty": 0,
                "answernotes": [
                    "prt1-1-T"
                ],
                "errors": [],
                "fverrors": [],
            },
        },
        "responsesummary": (
            "Seed: 683620564; "
            "ans1: 32 [valid]; prt1: !"
        ),
    }


def incorrect_payload() -> dict:
    return {
        "isgradable": True,
        "score": 0,
        "specificfeedback": "",
        "prts": {
            "prt1": (
                "<div class='incorrect'>"
                "Incorrect answer."
                "</div>"
            ),
        },
        "prtresults": {
            "prt1": {
                "score": 0,
                "penalty": 0.1,
                "answernotes": [
                    "prt1-1-F"
                ],
                "errors": [],
                "fverrors": [],
            },
        },
    }


def ungradable_payload() -> dict:
    return {
        "isgradable": False,
        "score": None,
        "prtresults": {},
        "responsesummary": (
            "The answer form could not be graded."
        ),
    }


def test_live_response_is_normalized() -> None:
    session = FakeSession(
        responses=[
            FakeResponse(
                correct_payload()
            )
        ]
    )

    client = HttpStackEvaluationClient(
        session=session
    )

    result = client.evaluate(
        build_request()
    )

    assert result.valid is True
    assert result.question_id == "207582"
    assert result.seed == 683620564
    assert len(result.prts) == 1

    prt = result.prts[0]

    assert prt.prt_name == "prt1"
    assert prt.score == 1.0
    assert prt.penalty == 0.0

    assert prt.answer_notes == [
        "prt1-1-T"
    ]

    assert "Correct answer" in (
        prt.feedback or ""
    )


def test_request_contains_xml_answers_and_seed() -> None:
    session = FakeSession(
        responses=[
            FakeResponse(
                correct_payload()
            )
        ]
    )

    client = HttpStackEvaluationClient(
        base_url="http://stack.test",
        timeout_seconds=45,
        session=session,
    )

    client.evaluate(
        build_request()
    )

    sent = session.requests[0]

    assert sent["url"] == (
        "http://stack.test/grade"
    )

    assert sent["json"]["answers"] == {
        "ans1": "32",
    }

    assert sent["json"]["seed"] == (
        683620564
    )

    assert "questionDefinition" in (
        sent["json"]
    )

    assert sent["timeout"] == 45


def test_incorrect_result_is_normalized() -> None:
    client = HttpStackEvaluationClient(
        session=FakeSession(
            responses=[
                FakeResponse(
                    incorrect_payload()
                )
            ]
        )
    )

    result = client.evaluate(
        build_request("25")
    )

    prt = result.prts[0]

    assert prt.score == 0.0

    assert prt.penalty == pytest.approx(
        0.1
    )

    assert prt.answer_notes == [
        "prt1-1-F"
    ]


def test_ungradable_response_becomes_invalid() -> None:
    client = HttpStackEvaluationClient(
        session=FakeSession(
            responses=[
                FakeResponse(
                    ungradable_payload()
                )
            ]
        )
    )

    result = client.evaluate(
        build_request("not-numeric")
    )

    assert result.valid is False


def test_api_error_message_is_preserved() -> None:
    client = HttpStackEvaluationClient(
        session=FakeSession(
            responses=[
                FakeResponse(
                    {
                        "message": (
                            "The question XML does "
                            "not contain deployed "
                            "variants"
                        )
                    },
                    ok=False,
                )
            ]
        )
    )

    with pytest.raises(
        StackApiResponseError,
        match="deployed variants",
    ):
        client.evaluate(
            build_request()
        )


def test_non_json_response_is_rejected() -> None:
    client = HttpStackEvaluationClient(
        session=FakeSession(
            responses=[
                FakeResponse(
                    {},
                    json_error=True,
                )
            ]
        )
    )

    with pytest.raises(
        StackApiResponseError,
        match="non-JSON",
    ):
        client.evaluate(
            build_request()
        )


def test_connection_error_is_wrapped() -> None:
    client = HttpStackEvaluationClient(
        session=FakeSession(
            error=requests.ConnectionError(
                "Connection refused"
            )
        )
    )

    with pytest.raises(
        StackApiConnectionError,
        match="Could not connect",
    ):
        client.evaluate(
            build_request()
        )


def test_decimal_retries_as_fraction() -> None:
    session = FakeSession(
        responses=[
            FakeResponse(
                ungradable_payload()
            ),
            FakeResponse(
                correct_payload()
            ),
        ]
    )

    client = HttpStackEvaluationClient(
        session=session
    )

    result = client.evaluate(
        build_request("3.75")
    )

    assert result.valid is True
    assert result.prts[0].score == 1.0

    assert len(session.requests) == 2

    assert (
        session.requests[0]
        ["json"]
        ["answers"]
        ["ans1"]
        == "3.75"
    )

    assert (
        session.requests[1]
        ["json"]
        ["answers"]
        ["ans1"]
        == "15/4"
    )


def test_half_retries_as_fraction() -> None:
    session = FakeSession(
        responses=[
            FakeResponse(
                ungradable_payload()
            ),
            FakeResponse(
                correct_payload()
            ),
        ]
    )

    client = HttpStackEvaluationClient(
        session=session
    )

    result = client.evaluate(
        build_request("0.5")
    )

    assert result.prts[0].score == 1.0

    assert (
        session.requests[1]
        ["json"]
        ["answers"]
        ["ans1"]
        == "1/2"
    )


def test_valid_incorrect_integer_is_not_retried() -> None:
    session = FakeSession(
        responses=[
            FakeResponse(
                incorrect_payload()
            )
        ]
    )

    client = HttpStackEvaluationClient(
        session=session
    )

    result = client.evaluate(
        build_request("540")
    )

    assert result.valid is True

    assert result.prts[0].score == 0.0

    assert len(session.requests) == 1

    assert (
        session.requests[0]
        ["json"]
        ["answers"]
        ["ans1"]
        == "540"
    )


def test_non_numeric_answer_is_not_retried() -> None:
    session = FakeSession(
        responses=[
            FakeResponse(
                ungradable_payload()
            )
        ]
    )

    client = HttpStackEvaluationClient(
        session=session
    )

    result = client.evaluate(
        build_request("x + 1")
    )

    assert result.valid is False

    assert len(session.requests) == 1


def test_existing_fraction_is_not_retried_when_valid() -> None:
    session = FakeSession(
        responses=[
            FakeResponse(
                correct_payload()
            )
        ]
    )

    client = HttpStackEvaluationClient(
        session=session
    )

    result = client.evaluate(
        build_request("15/4")
    )

    assert result.prts[0].score == 1.0

    assert len(session.requests) == 1



def test_null_prt_score_is_preserved() -> None:
    payload = correct_payload()

    payload["prtresults"]["prt1"][
        "score"
    ] = None

    payload["prtresults"]["prt1"][
        "penalty"
    ] = None

    client = HttpStackEvaluationClient(
        session=FakeSession(
            responses=[
                FakeResponse(payload)
            ]
        )
    )

    result = client.evaluate(
        build_request()
    )

    assert result.valid is True
    assert result.overall_score == 1.0

    assert result.prts[0].score is None

    assert (
        result.prts[0].penalty
        is None
    )


def test_zero_overall_score_survives_null_prt_score(
) -> None:
    payload = incorrect_payload()

    payload["prtresults"]["prt1"][
        "score"
    ] = None

    client = HttpStackEvaluationClient(
        session=FakeSession(
            responses=[
                FakeResponse(payload)
            ]
        )
    )

    result = client.evaluate(
        build_request("25")
    )

    assert result.valid is True
    assert result.overall_score == 0.0
    assert result.prts[0].score is None
