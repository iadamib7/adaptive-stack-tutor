from backend.app.database.init_db import initialize_database
from backend.app.database.student_progress_repository import (
    StudentProgressRepository,
)
from backend.app.learning.assessment.answer_evaluator import AnswerEvaluator
from backend.app.learning.assessment.evaluation_result import EvaluationResult
from backend.app.learning.question_bank.question import Question
from backend.app.learning.question_bank.repository import QuestionRepository
from backend.app.learning.recommendation.engine import RecommendationEngine
from backend.app.learning.student_model.attempt import Attempt
from backend.app.learning.student_model.student import Student
from backend.app.learning.student_model.tracker import StudentTracker
from backend.app.schemas.attempts import AdaptiveLearningResponse


class AdaptiveLearningService:
    MASTERY_THRESHOLD = 0.85

    def __init__(
        self,
        repository: QuestionRepository,
        progress_repository: StudentProgressRepository | None = None,
    ) -> None:
        initialize_database()

        self.repository = repository
        self.tracker = StudentTracker()
        self.answer_evaluator = AnswerEvaluator()
        self.recommendation_engine = RecommendationEngine(repository)

        self.progress_repository = (
            progress_repository
            if progress_repository is not None
            else StudentProgressRepository()
        )

    def process_submission(
        self,
        student_id: int,
        student_name: str,
        question_id: int,
        response: str,
        course: str | None = None,
    ) -> AdaptiveLearningResponse:
        question = self.repository.get_by_id(question_id)

        if question is None:
            raise ValueError("Question not found.")

        student = self.progress_repository.get_student(student_id)

        if student is None:
            student = Student(
                id=student_id,
                name=student_name,
            )
        else:
            student.name = student_name

        mastery_before = student.mastery.get(
            question.concept,
            0.5,
        )

        evaluation = self.answer_evaluator.evaluate(
            student_answer=response,
            expected_answer=question.correct_answer,
        )

        attempt = Attempt(
            student_id=student_id,
            question_id=question_id,
            concept=question.concept,
            correct=evaluation.correct,
            response=response,
        )

        self.tracker.process_attempt(
            student=student,
            attempt=attempt,
        )

        mastery_after = student.mastery[question.concept]

        self.progress_repository.save_progress(
            student=student,
            attempt=attempt,
        )

        concept_mastered = (
            mastery_after >= self.MASTERY_THRESHOLD
        )

        feedback = self._generate_feedback(
            question=question,
            evaluation=evaluation,
            mastery_after=mastery_after,
            concept_mastered=concept_mastered,
        )

        attempted_question_ids = (
            self.progress_repository.get_attempted_question_ids(
                student_id
            )
        )

        if concept_mastered:
            recommendation = (
                self.recommendation_engine.recommend_next_question(
                    student=student,
                    attempted_question_ids=attempted_question_ids,
                    course=course or question.course,
                )
            )
        else:
            recommendation = (
                self.recommendation_engine.recommend_next_question(
                    student=student,
                    attempted_question_ids=attempted_question_ids,
                    course=course or question.course,
                    target_concept=question.concept,
                    exclude_question_id=question.id,
                )
            )

        recommendation_reason = self._build_recommendation_reason(
            question=question,
            concept_mastered=concept_mastered,
            default_reason=(
                recommendation.reason
                if recommendation is not None
                else None
            ),
        )

        return AdaptiveLearningResponse(
            student=student,
            submitted_question_id=question.id,
            submitted_concept=question.concept,
            student_response=response,
            expected_answer=question.correct_answer,
            correct=evaluation.correct,
            feedback=feedback,
            evaluation_error=evaluation.error_message,
            mastery_before=mastery_before,
            mastery_after=mastery_after,
            concept_mastered=concept_mastered,
            next_question=(
                recommendation.question
                if recommendation is not None
                else None
            ),
            recommendation_reason=recommendation_reason,
        )

    def get_student(
        self,
        student_id: int,
    ) -> Student | None:
        return self.progress_repository.get_student(student_id)

    def get_attempt_history(
        self,
        student_id: int,
    ) -> list[Attempt]:
        return self.progress_repository.get_attempt_history(student_id)

    @staticmethod
    def _generate_feedback(
        question: Question,
        evaluation: EvaluationResult,
        mastery_after: float,
        concept_mastered: bool,
    ) -> str:
        mastery_percentage = round(mastery_after * 100)

        if evaluation.error_message is not None:
            return (
                f"{evaluation.error_message} "
                "Check your mathematical notation and try again. "
                f"This question is testing {question.concept}."
            )

        if evaluation.correct:
            if concept_mastered:
                return (
                    f"Correct. You successfully applied "
                    f"{question.concept}. Your mastery is now "
                    f"approximately {mastery_percentage}%, so you are "
                    "ready to progress to another concept or level."
                )

            return (
                f"Correct. You applied {question.concept} successfully. "
                f"Your mastery is now approximately "
                f"{mastery_percentage}%. You will receive another "
                "question testing the same concept so the system can "
                "confirm that your understanding is consistent."
            )

        feedback_parts = [
            "Your answer is not mathematically equivalent to the "
            "expected answer.",
            f"This question is testing {question.concept}.",
        ]

        if question.learning_outcome:
            feedback_parts.append(
                f"Focus on this learning goal: "
                f"{question.learning_outcome}"
            )

        if question.common_errors:
            feedback_parts.append(
                "Check for this common mistake: "
                f"{question.common_errors[0]}"
            )

        if question.remediation_concept:
            feedback_parts.append(
                f"Review {question.remediation_concept} before your "
                "next attempt."
            )
        elif question.prerequisite:
            feedback_parts.append(
                f"It may help to review the prerequisite concept: "
                f"{question.prerequisite}."
            )

        feedback_parts.append(
            f"The expected answer is {question.correct_answer}. "
            "Compare it with your response and identify which operation "
            "or rule was missing."
        )

        feedback_parts.append(
            "Your next question will be different, but it will test "
            "the same concept."
        )

        return " ".join(feedback_parts)

    @staticmethod
    def _build_recommendation_reason(
        question: Question,
        concept_mastered: bool,
        default_reason: str | None,
    ) -> str | None:
        if concept_mastered:
            return (
                f"You reached the mastery threshold for "
                f"{question.concept}. The system is now selecting the "
                "next appropriate learning target."
            )

        return (
            f"Continue practicing {question.concept}. The next question "
            "is different, but it tests the same mathematical concept. "
            f"{default_reason or ''}"
        ).strip()