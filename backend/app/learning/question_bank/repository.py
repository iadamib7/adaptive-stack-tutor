from .question import DifficultyLevel, Question


class QuestionRepository:
    def __init__(self, questions: list[Question]) -> None:
        self._questions = questions

    def get_all(self) -> list[Question]:
        return self._questions.copy()

    def get_by_id(self, question_id: int) -> Question | None:
        return next(
            (
                question
                for question in self._questions
                if question.id == question_id
            ),
            None,
        )

    def filter_questions(
        self,
        course: str | None = None,
        topic: str | None = None,
        concept: str | None = None,
        difficulty: DifficultyLevel | None = None,
        prerequisite: str | None = None,
    ) -> list[Question]:
        results = self._questions

        if course is not None:
            results = [
                question
                for question in results
                if question.course.lower() == course.lower()
            ]

        if topic is not None:
            results = [
                question
                for question in results
                if question.topic.lower() == topic.lower()
            ]

        if concept is not None:
            results = [
                question
                for question in results
                if question.concept.lower() == concept.lower()
            ]

        if difficulty is not None:
            results = [
                question
                for question in results
                if question.difficulty == difficulty
            ]

        if prerequisite is not None:
            results = [
                question
                for question in results
                if question.prerequisite is not None
                and question.prerequisite.lower() == prerequisite.lower()
            ]

        return results