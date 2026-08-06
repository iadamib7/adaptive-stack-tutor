from fastapi import APIRouter, HTTPException

from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackPRTResult,
)
from backend.app.learning.session.models import (
    LearningSessionState,
)
from backend.app.schemas.sessions import (
    StartSessionRequest,
    SubmitSessionAnswerRequest,
)
from backend.app.services.session_service_factory import (
    session_service,
    stack_client,
)


router = APIRouter(
    prefix="/sessions",
    tags=["Curriculum-Aware Sessions"],
)


@router.post(
    "/start",
    response_model=LearningSessionState,
)
def start_session(
    request: StartSessionRequest,
) -> LearningSessionState:
    try:
        return session_service.start_session(
            student_id=request.student_id,
            concept_id=request.concept_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post(
    "/submit-answer",
    response_model=LearningSessionState,
)
def submit_answer(
    request: SubmitSessionAnswerRequest,
) -> LearningSessionState:
    """
    Development endpoint.

    The request currently includes the normalized result that
    STACK would return. Once the real STACK HTTP client is added,
    score, answer note and feedback will come directly from STACK.
    """

    stack_result = NormalizedStackResult(
        question_id=request.question_id,
        valid=True,
        seed=request.seed,
        prts=[
            StackPRTResult(
                prt_name=request.prt_name,
                score=request.score,
                penalty=request.penalty,
                answer_notes=[
                    request.answer_note
                ],
                feedback=request.feedback,
            )
        ],
    )

    stack_client.register_result(stack_result)

    try:
        return session_service.submit_answer(
            student_id=request.student_id,
            concept_id=request.concept_id,
            question_id=request.question_id,
            question_xml=(
                "<question type='stack'></question>"
            ),
            student_answers=(
                request.student_answers
            ),
            target_prt_name=request.prt_name,
            seed=request.seed,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.get(
    "/{student_id}",
    response_model=LearningSessionState,
)
def get_session(
    student_id: int,
) -> LearningSessionState:
    session = session_service.get_session(
        student_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Learning session not found.",
        )

    return session
