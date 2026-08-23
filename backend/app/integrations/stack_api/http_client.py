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
from backend.app.learning.answer_normalization.numeric import (
    canonicalize_numeric_answer,
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

    Learner answers are always submitted to STACK exactly as
    entered first.

    If STACK cannot produce a meaningful grading result for a
    simple numeric answer, the client may retry once using an
    exact canonical fraction representation.

    Example:

        3.75
            ->
        STACK cannot grade decimal form
            ->
        15/4
            ->
        retry STACK

    Incorrect but otherwise valid learner answers are never
    rewritten merely to make them correct.
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
            "answers": dict(
                request.student_answers
            ),
        }

        if request.seed is not None:
            payload["seed"] = request.seed

        response_payload = self._send_grade_request(
            payload
        )

        if self._needs_numeric_retry(
            response_payload
        ):
            normalized_answers = (
                self._build_numeric_fallback_answers(
                    request.student_answers
                )
            )

            if normalized_answers is not None:
                retry_payload = dict(payload)

                retry_payload["answers"] = (
                    normalized_answers
                )

                retry_response = (
                    self._send_grade_request(
                        retry_payload
                    )
                )

                if self._has_meaningful_result(
                    retry_response
                ):
                    response_payload = (
                        retry_response
                    )

        return self._normalize_response(
            question_id=request.question_id,
            seed=request.seed,
            payload=response_payload,
        )

    def _send_grade_request(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
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

        return self._read_response(
            response
        )

    @staticmethod
    def _needs_numeric_retry(
        payload: dict[str, Any],
    ) -> bool:
        """
        Retry only when STACK failed to produce a meaningful
        mathematical grading result.

        A normal incorrect result with score 0 and a PRT result
        must NOT trigger normalization.
        """

        if not bool(
            payload.get(
                "isgradable",
                False,
            )
        ):
            return True

        score = payload.get("score")

        if not isinstance(
            score,
            (int, float),
        ):
            return True

        prt_results = payload.get(
            "prtresults"
        )

        if (
            not isinstance(
                prt_results,
                dict,
            )
            or not prt_results
        ):
            return True

        return False

    @staticmethod
    def _has_meaningful_result(
        payload: dict[str, Any],
    ) -> bool:
        if not bool(
            payload.get(
                "isgradable",
                False,
            )
        ):
            return False

        score = payload.get("score")

        if not isinstance(
            score,
            (int, float),
        ):
            return False

        prt_results = payload.get(
            "prtresults"
        )

        return (
            isinstance(
                prt_results,
                dict,
            )
            and bool(prt_results)
        )

    @staticmethod
    def _build_numeric_fallback_answers(
        student_answers: dict[str, str],
    ) -> dict[str, str] | None:
        """
        Canonicalize only simple numeric answers.

        If none of the learner's answers can be safely changed
        to a different exact numeric representation, no retry
        should occur.
        """

        normalized = dict(
            student_answers
        )

        changed = False

        for (
            input_name,
            answer,
        ) in student_answers.items():
            canonical = (
                canonicalize_numeric_answer(
                    answer
                )
            )

            if canonical is None:
                continue

            if canonical == answer.strip():
                continue

            normalized[input_name] = (
                canonical
            )

            changed = True

        if not changed:
            return None

        return normalized

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
            payload.get(
                "isgradable",
                False,
            )
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
                    payload.get(
                        "specificfeedback"
                    )
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

        if not isinstance(
            raw_prt_results,
            dict,
        ):
            raise StackApiResponseError(
                "STACK returned invalid PRT results."
            )

        if not isinstance(
            raw_prt_feedback,
            dict,
        ):
            raw_prt_feedback = {}

        prts: list[StackPRTResult] = []

        for (
            prt_name,
            raw_result,
        ) in raw_prt_results.items():
            if not isinstance(
                raw_result,
                dict,
            ):
                raise StackApiResponseError(
                    f"STACK returned an invalid result "
                    f"for PRT {prt_name}."
                )

            answer_notes = (
                raw_result.get(
                    "answernotes",
                    [],
                )
            )

            raw_errors = raw_result.get(
                "errors",
                [],
            )

            raw_fv_errors = raw_result.get(
                "fverrors",
                [],
            )

            if not isinstance(
                raw_errors,
                list,
            ):
                raw_errors = []

            if not isinstance(
                raw_fv_errors,
                list,
            ):
                raw_fv_errors = []

            errors = [
                *raw_errors,
                *raw_fv_errors,
            ]

            if not isinstance(
                answer_notes,
                list,
            ):
                answer_notes = []

            prts.append(
                StackPRTResult(
                    prt_name=str(
                        prt_name
                    ),
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
                        for note
                        in answer_notes
                    ],
                    feedback=(
                        raw_prt_feedback.get(
                            prt_name
                        )
                    ),
                    errors=[
                        str(error)
                        for error
                        in errors
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
