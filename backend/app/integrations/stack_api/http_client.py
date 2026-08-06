from typing import Any

import requests

from backend.app.integrations.stack_api.client import (
    StackEvaluationClient,
)
from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackEvaluationRequest,
    StackPRTResult,
)


class StackApiConnectionError(RuntimeError):
    pass


class StackApiResponseError(RuntimeError):
    pass


class HttpStackEvaluationClient(
    StackEvaluationClient
):
    """
    Evaluate STACK questions through the standalone HTTP API.

    The client sends Moodle XML and learner answers to /grade,
    then converts the live response into NormalizedStackResult.
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

    def evaluate(
        self,
        request: StackEvaluationRequest,
    ) -> NormalizedStackResult:
        payload: dict[str, Any] = {
            "questionDefinition": (
                request.question_xml
            ),
            "answers": request.student_answers,
        }

        if request.seed is not None:
            payload["seed"] = request.seed

        try:
            response = self.session.post(
                f"{self.base_url}/grade",
                json=payload,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as error:
            raise StackApiConnectionError(
                "Could not connect to the STACK API at "
                f"{self.base_url}."
            ) from error

        response_payload = self._read_response(
            response
        )

        return self._normalize_response(
            question_id=request.question_id,
            seed=request.seed,
            payload=response_payload,
        )

    @staticmethod
    def _read_response(
        response: requests.Response,
    ) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as error:
            raise StackApiResponseError(
                "STACK returned a non-JSON response."
            ) from error

        if not isinstance(payload, dict):
            raise StackApiResponseError(
                "STACK returned an unexpected JSON "
                "response."
            )

        if not response.ok:
            message = payload.get(
                "message",
                "STACK grading failed.",
            )

            raise StackApiResponseError(
                str(message)
            )

        return payload

    @staticmethod
    def _normalize_response(
        question_id: str,
        seed: int | None,
        payload: dict[str, Any],
    ) -> NormalizedStackResult:
        is_gradable = bool(
            payload.get("isgradable", False)
        )

        if not is_gradable:
            message = payload.get(
                "responsesummary",
                "The learner response could not be graded.",
            )

            return NormalizedStackResult(
                question_id=question_id,
                valid=False,
                seed=seed,
                validation_errors=[
                    str(message)
                ],
                raw_feedback=(
                    payload.get("specificfeedback")
                ),
            )

        raw_prt_results = payload.get(
            "prtresults",
            {},
        )

        raw_prt_feedback = payload.get(
            "prts",
            {},
        )

        if not isinstance(raw_prt_results, dict):
            raise StackApiResponseError(
                "STACK returned invalid PRT results."
            )

        if not isinstance(raw_prt_feedback, dict):
            raw_prt_feedback = {}

        prts: list[StackPRTResult] = []

        for (
            prt_name,
            raw_result,
        ) in raw_prt_results.items():
            if not isinstance(raw_result, dict):
                raise StackApiResponseError(
                    f"STACK returned an invalid result "
                    f"for PRT {prt_name}."
                )

            answer_notes = raw_result.get(
                "answernotes",
                [],
            )

            errors = [
                *raw_result.get(
                    "errors",
                    [],
                ),
                *raw_result.get(
                    "fverrors",
                    [],
                ),
            ]

            prts.append(
                StackPRTResult(
                    prt_name=str(prt_name),
                    score=float(
                        raw_result.get(
                            "score",
                            0.0,
                        )
                    ),
                    penalty=float(
                        raw_result.get(
                            "penalty",
                            0.0,
                        )
                    ),
                    answer_notes=[
                        str(note)
                        for note in answer_notes
                    ],
                    feedback=raw_prt_feedback.get(
                        prt_name
                    ),
                    errors=[
                        str(error)
                        for error in errors
                    ],
                )
            )

        return NormalizedStackResult(
            question_id=question_id,
            valid=True,
            seed=seed,
            prts=prts,
            raw_feedback=payload.get(
                "specificfeedback"
            ),
        )
