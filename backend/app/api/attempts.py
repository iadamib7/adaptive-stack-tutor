from fastapi import APIRouter, HTTPException

from backend.app.api.questions import repository
from backend.app.learning.student_model.attempt import Attempt
from backend.app.learning.student_model.student import Student
from backend.app.schemas.attempts import (
    AdaptiveLearningResponse,
    AttemptSubmission,
)
from backend.app.services.adaptive_learning_service import (
    AdaptiveLearningService,
)

router = APIRouter(
    prefix="/learning",
    tags=["Adaptive Learning"],
)

service = AdaptiveLearningService(repository)


@router.post(
    "/attempts",
    response_model=AdaptiveLearningResponse,
)
def submit_attempt(
    submission: AttemptSubmission,
) -> AdaptiveLearningResponse:
    try:
        return service.process_submission(
            student_id=submission.student_id,
            student_name=submission.student_name,
            question_id=submission.question_id,
            response=submission.response,
            correct=submission.correct,
            course=submission.course,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.get(
    "/students/{student_id}",
    response_model=Student,
)
def get_student(student_id: int) -> Student:
    student = service.get_student(student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student


@router.get(
    "/students/{student_id}/attempts",
    response_model=list[Attempt],
)
def get_student_attempts(
    student_id: int,
) -> list[Attempt]:
    student = service.get_student(student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return service.get_attempt_history(student_id)