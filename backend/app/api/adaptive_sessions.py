from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.integrations.stack_api.http_client import (
    HttpStackEvaluationClient,
)

from backend.app.learning.adaptive_engine.session_service import (
    GenericAdaptiveSessionService,
)

from backend.app.learning.adaptive_engine.stack_runtime import (
    AdaptiveStackRenderer,
)


router = APIRouter(
    prefix="/api/adaptive",
    tags=["adaptive"],
)


class CreateAdaptiveSessionRequest(
    BaseModel
):
    learner_id: int

    question_bank_xml: str = Field(
        min_length=1,
    )

    metadata_json: str | None = None


class SubmitAdaptiveAnswerRequest(
    BaseModel
):
    learner_id: int

    answers: dict[str, str] = Field(
        min_length=1,
    )


class AdaptiveQuestionResponse(
    BaseModel
):
    session_id: str

    learner_id: int

    question_id: str
    title: str

    seed: int

    html: str

    inputs: dict[
        str,
        object,
    ]

    ability: float

    decision_reason: str

    previous_score: float | None = None

    previous_outcome: str | None = None


_sessions: dict[
    str,
    GenericAdaptiveSessionService,
] = {}


def _build_response(
    *,
    session_id: str,
    view,
) -> AdaptiveQuestionResponse:
    return AdaptiveQuestionResponse(
        session_id=session_id,
        learner_id=view.learner_id,
        question_id=view.question_id,
        title=view.title,
        seed=view.seed,
        html=view.html,
        inputs=view.inputs,
        ability=view.ability,
        decision_reason=(
            view.decision_reason
        ),
        previous_score=(
            view.previous_score
        ),
        previous_outcome=(
            view.previous_outcome
        ),
    )


@router.post(
    "/sessions",
    response_model=(
        AdaptiveQuestionResponse
    ),
)
def create_adaptive_session(
    request:
        CreateAdaptiveSessionRequest,
) -> AdaptiveQuestionResponse:
    """
    Create a curriculum-independent adaptive
    session directly from instructor-authored
    STACK/Moodle XML.
    """

    try:
        service = (
            GenericAdaptiveSessionService
            .from_xml(
                xml_text=(
                    request
                    .question_bank_xml
                ),
                metadata_json=(
                    request
                    .metadata_json
                ),
                evaluation_client=(
                    HttpStackEvaluationClient()
                ),
                renderer=(
                    AdaptiveStackRenderer()
                ),
            )
        )

        view = service.start(
            learner_id=(
                request.learner_id
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    session_id = str(
        uuid4()
    )

    _sessions[
        session_id
    ] = service

    return _build_response(
        session_id=session_id,
        view=view,
    )


@router.post(
    "/sessions/{session_id}/answers",
    response_model=(
        AdaptiveQuestionResponse
    ),
)
def submit_adaptive_answer(
    session_id: str,
    request:
        SubmitAdaptiveAnswerRequest,
) -> AdaptiveQuestionResponse:
    service = _sessions.get(
        session_id
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Adaptive session "
                "not found."
            ),
        )

    try:
        view = service.submit_answer(
            learner_id=(
                request.learner_id
            ),
            student_answers=(
                request.answers
            ),
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return _build_response(
        session_id=session_id,
        view=view,
    )


@router.get(
    "/health"
)
def adaptive_health() -> dict[
    str,
    str,
]:
    return {
        "status": "healthy",
        "mode": (
            "curriculum-independent"
        ),
    }
