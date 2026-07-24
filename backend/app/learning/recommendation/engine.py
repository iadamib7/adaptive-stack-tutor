from dataclasses import dataclass

from backend.app.learning.question_bank.question import Question
from backend.app.learning.question_bank.repository import QuestionRepository
from backend.app.learning.student_model.student import Student

from .strategy import mastery_to_difficulty


@dataclass
class Recommendation:
    question: Question
    reason: str
    target_concept: str
    mastery_score: float


class RecommendationEngine:
    def __init__(self, repository: QuestionRepository) -> None:
        self.repository = repository

    def recommend_next_question(
        self,
        student: Student,
        attempted_question_ids: set[int] | None = None,
        course: str | None = None,
    ) -> Recommendation | None:
        attempted_ids = attempted_question_ids or set()

        available_questions = self.repository.get_all()

        if course is not None:
            available_questions = [
                question
                for question in available_questions
                if question.course.lower() == course.lower()
            ]

        if not available_questions:
            return None

        target_concept, mastery_score = self._find_target_concept(
            student=student,
            questions=available_questions,
        )

        target_difficulty = mastery_to_difficulty(mastery_score)

        matching_questions = [
            question
            for question in available_questions
            if question.concept.lower() == target_concept.lower()
            and question.difficulty == target_difficulty
            and question.id not in attempted_ids
        ]

        if not matching_questions:
            matching_questions = [
                question
                for question in available_questions
                if question.concept.lower() == target_concept.lower()
                and question.id not in attempted_ids
            ]

        if not matching_questions:
            matching_questions = [
                question
                for question in available_questions
                if question.concept.lower() == target_concept.lower()
            ]

        if not matching_questions:
            matching_questions = [
                question
                for question in available_questions
                if question.id not in attempted_ids
            ]

        if not matching_questions:
            matching_questions = available_questions

        selected_question = min(
            matching_questions,
            key=lambda question: abs(
                question.difficulty.value - target_difficulty.value
            ),
        )

        return Recommendation(
            question=selected_question,
            reason=(
                f"Recommended because {target_concept} is currently "
                f"one of the student's weakest concepts."
            ),
            target_concept=target_concept,
            mastery_score=mastery_score,
        )

    def _find_target_concept(
        self,
        student: Student,
        questions: list[Question],
    ) -> tuple[str, float]:
        available_concepts = {
            question.concept
            for question in questions
        }

        known_concepts = {
            concept: score
            for concept, score in student.mastery.items()
            if concept in available_concepts
        }

        if known_concepts:
            return min(
                known_concepts.items(),
                key=lambda item: item[1],
            )

        first_question = min(
            questions,
            key=lambda question: question.difficulty.value,
        )

        return first_question.concept, 0.5
    