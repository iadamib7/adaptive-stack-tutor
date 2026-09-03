from __future__ import annotations

from dataclasses import dataclass

import requests


class AdaptiveStackRenderError(
    RuntimeError
):
    pass


@dataclass(frozen=True)
class RenderedAdaptiveQuestion:
    question_id: str
    seed: int
    html: str
    inputs: dict[str, object]
    feedback: str | None = None


class AdaptiveStackRenderer:
    """
    Render instructor-provided STACK XML directly.

    This runtime has no knowledge of:
    - curriculum;
    - concepts;
    - national standards;
    - knowledge graphs.
    """

    def __init__(
        self,
        *,
        base_url: str = (
            "http://localhost:3080"
        ),
        timeout_seconds: int = 120,
        session: (
            requests.Session | None
        ) = None,
    ) -> None:
        self.base_url = (
            base_url.rstrip("/")
        )

        self.timeout_seconds = (
            timeout_seconds
        )

        self.session = (
            session
            if session is not None
            else requests.Session()
        )

    def render(
        self,
        *,
        question_id: str,
        question_xml: str,
        seed: int,
    ) -> RenderedAdaptiveQuestion:
        response = self.session.post(
            f"{self.base_url}/render",
            json={
                "questionDefinition":
                    question_xml,
                "seed": seed,
                "renderInputs":
                    "student-",
                "fullRender": [
                    "validation-",
                    "feedback-",
                ],
                "readOnly": False,
            },
            timeout=self.timeout_seconds,
        )

        try:
            payload = response.json()
        except ValueError as error:
            raise AdaptiveStackRenderError(
                "STACK returned a non-JSON "
                "render response."
            ) from error

        if not response.ok:
            raise AdaptiveStackRenderError(
                str(
                    payload.get(
                        "message",
                        "STACK render failed.",
                    )
                )
            )

        if not isinstance(
            payload,
            dict,
        ):
            raise AdaptiveStackRenderError(
                "STACK returned an invalid "
                "render response."
            )

        inputs = payload.get(
            "questioninputs",
            {},
        )

        if not isinstance(
            inputs,
            dict,
        ):
            raise AdaptiveStackRenderError(
                "STACK returned invalid "
                "question inputs."
            )

        return RenderedAdaptiveQuestion(
            question_id=question_id,
            seed=seed,
            html=str(
                payload.get(
                    "questionrender",
                    "",
                )
            ),
            inputs=inputs,
            feedback=payload.get(
                "specificfeedback"
            ),
        )
