from pydantic import BaseModel, Field

from backend.app.learning.question_bank.question import Question
from backend.app.learning.student_model.student import Student


class AttemptSubmission(BaseModel):
    student_id: int = Field(gt=0)
    student_name: str = Field(min_length=1)
    question_id: int = Field(gt=0)
    response: str = Field(min_length=1)
    correct: bool
    course: str | None = None


class AdaptiveLearningResponse(BaseModel):
    student: Student
    submitted_question_id: int
    submitted_concept: str
    mastery_before: float
    mastery_after: float
    next_question: Question | None
    recommendation_reason: str | None