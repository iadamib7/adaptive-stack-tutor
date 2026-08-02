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
        target_concept: str | None = None,
        exclude_question_id: int | None = None,
    ) -> Recommendation | None:
        attempted_ids = set(attempted_question_ids or set())

        if exclude_question_id is not None:
            attempted_ids.add(exclude_question_id)

        available_questions = self.repository.get_all()

        if course is not None:
            available_questions = [
                question
                for question in available_questions
                if question.course.lower() == course.lower()
            ]

        if not available_questions:
            return None

        if target_concept is None:
            selected_concept, mastery_score = self._find_target_concept(
                student=student,
                questions=available_questions,
            )
        else:
            selected_concept = target_concept
            mastery_score = student.mastery.get(target_concept, 0.0)

        target_difficulty = mastery_to_difficulty(mastery_score)

        concept_questions = [
            question
            for question in available_questions
            if question.concept.lower() == selected_concept.lower()
        ]

        if not concept_questions:
            return None

        matching_questions = [
            question
            for question in concept_questions
            if question.difficulty == target_difficulty
            and question.id not in attempted_ids
        ]

        if not matching_questions:
            matching_questions = [
                question
                for question in concept_questions
                if question.id not in attempted_ids
            ]

        if not matching_questions:
            matching_questions = concept_questions

        selected_question = min(
            matching_questions,
            key=lambda question: (
                abs(
                    question.difficulty.value
                    - target_difficulty.value
                ),
                question.id,
            ),
        )

        return Recommendation(
            question=selected_question,
            reason=self._build_reason(
                target_concept=selected_concept,
                mastery_score=mastery_score,
            ),
            target_concept=selected_concept,
            mastery_score=mastery_score,
        )

    @staticmethod
    def _build_reason(
        target_concept: str,
        mastery_score: float,
    ) -> str:
        mastery_percentage = round(mastery_score * 100)

        return (
            f"Continue practicing {target_concept}. "
            f"Current mastery is approximately "
            f"{mastery_percentage}%, so the next question tests "
            f"the same concept at an appropriate difficulty level."
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

        return first_question.concept, 0.0
    