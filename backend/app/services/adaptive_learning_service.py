from backend.app.learning.question_bank.repository import QuestionRepository
from backend.app.learning.recommendation.engine import RecommendationEngine
from backend.app.learning.student_model.attempt import Attempt
from backend.app.learning.student_model.student import Student
from backend.app.learning.student_model.tracker import StudentTracker
from backend.app.schemas.attempts import AdaptiveLearningResponse


class AdaptiveLearningService:
    def __init__(self, repository: QuestionRepository) -> None:
        self.repository = repository
        self.tracker = StudentTracker()
        self.recommendation_engine = RecommendationEngine(repository)

        self._students: dict[int, Student] = {}
        self._attempted_question_ids: dict[int, set[int]] = {}
        self._attempt_history: dict[int, list[Attempt]] = {}

    def process_submission(
        self,
        student_id: int,
        student_name: str,
        question_id: int,
        response: str,
        correct: bool,
        course: str | None = None,
    ) -> AdaptiveLearningResponse:
        question = self.repository.get_by_id(question_id)

        if question is None:
            raise ValueError("Question not found.")

        student = self._students.get(student_id)

        if student is None:
            student = Student(
                id=student_id,
                name=student_name,
            )
            self._students[student_id] = student

        mastery_before = student.mastery.get(
            question.concept,
            0.5,
        )

        attempt = Attempt(
            student_id=student_id,
            question_id=question_id,
            concept=question.concept,
            correct=correct,
            response=response,
        )

        self.tracker.process_attempt(
            student=student,
            attempt=attempt,
        )

        self._attempted_question_ids.setdefault(
            student_id,
            set(),
        ).add(question_id)

        self._attempt_history.setdefault(
            student_id,
            [],
        ).append(attempt)

        recommendation = (
            self.recommendation_engine.recommend_next_question(
                student=student,
                attempted_question_ids=self._attempted_question_ids[
                    student_id
                ],
                course=course or question.course,
            )
        )

        return AdaptiveLearningResponse(
            student=student,
            submitted_question_id=question.id,
            submitted_concept=question.concept,
            mastery_before=mastery_before,
            mastery_after=student.mastery[question.concept],
            next_question=(
                recommendation.question
                if recommendation is not None
                else None
            ),
            recommendation_reason=(
                recommendation.reason
                if recommendation is not None
                else None
            ),
        )

    def get_student(self, student_id: int) -> Student | None:
        return self._students.get(student_id)

    def get_attempt_history(
        self,
        student_id: int,
    ) -> list[Attempt]:
        return self._attempt_history.get(
            student_id,
            [],
        ).copy()