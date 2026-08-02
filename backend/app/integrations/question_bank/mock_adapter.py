from backend.app.integrations.question_bank.models import (
    CurriculumStage,
    QuestionMetadata,
)


class MockQuestionBankAdapter:
    """
    Temporary question-bank implementation used to develop and test
    sequencing logic before the real STACK/OSQB API is available.

    These questions are development fixtures, not the final Ghanaian
    mathematics question bank.
    """

    def __init__(
        self,
        questions: list[QuestionMetadata] | None = None,
    ) -> None:
        self._questions = questions or self._build_fixture_questions()

    def get_question(
        self,
        question_id: str,
    ) -> QuestionMetadata | None:
        return next(
            (
                question
                for question in self._questions
                if question.id == question_id
            ),
            None,
        )

    def find_questions(
        self,
        *,
        concept: str | None = None,
        topic: str | None = None,
        difficulty: int | None = None,
        curriculum_stage: CurriculumStage | None = None,
    ) -> list[QuestionMetadata]:
        results = self._questions

        if concept is not None:
            results = [
                question
                for question in results
                if question.concept.casefold() == concept.casefold()
            ]

        if topic is not None:
            results = [
                question
                for question in results
                if question.topic.casefold() == topic.casefold()
            ]

        if difficulty is not None:
            results = [
                question
                for question in results
                if question.difficulty == difficulty
            ]

        if curriculum_stage is not None:
            results = [
                question
                for question in results
                if question.curriculum_stage == curriculum_stage
            ]

        return results.copy()

    @staticmethod
    def _build_fixture_questions() -> list[QuestionMetadata]:
        return [
            QuestionMetadata(
                id="JHS-INT-001",
                title="Integer Operations Foundation",
                question_text="Evaluate: -4 + 9.",
                topic="Number",
                concept="Integer Operations",
                sub_concept="Addition of integers",
                curriculum_stage=CurriculumStage.JHS,
                difficulty=1,
                learning_outcomes=[
                    "Add positive and negative integers."
                ],
            ),
            QuestionMetadata(
                id="JHS-ALG-001",
                title="One-Step Linear Equation",
                question_text="Solve: x + 5 = 12.",
                topic="Algebra",
                concept="Linear Equations",
                sub_concept="One-step equations",
                curriculum_stage=CurriculumStage.JHS,
                difficulty=1,
                prerequisites=["Integer Operations"],
                learning_outcomes=[
                    "Solve a one-step linear equation."
                ],
            ),
            QuestionMetadata(
                id="JHS-ALG-002",
                title="Two-Step Linear Equation",
                question_text="Solve: 3x + 2 = 14.",
                topic="Algebra",
                concept="Linear Equations",
                sub_concept="Two-step equations",
                curriculum_stage=CurriculumStage.JHS,
                difficulty=2,
                prerequisites=[
                    "Integer Operations",
                    "One-Step Linear Equations",
                ],
                learning_outcomes=[
                    "Solve a two-step linear equation."
                ],
            ),
            QuestionMetadata(
                id="JHS-ALG-003",
                title="Linear Equation with Negative Terms",
                question_text="Solve: 2x - 7 = 9.",
                topic="Algebra",
                concept="Linear Equations",
                sub_concept="Equations involving negative terms",
                curriculum_stage=CurriculumStage.JHS,
                difficulty=3,
                prerequisites=[
                    "Integer Operations",
                    "Two-Step Linear Equations",
                ],
                learning_outcomes=[
                    "Solve equations involving negative terms."
                ],
            ),
            QuestionMetadata(
                id="SHS-ALG-001",
                title="Introductory Simultaneous Equations",
                question_text=(
                    "Solve the system: x + y = 7 and x - y = 1."
                ),
                topic="Algebra",
                concept="Simultaneous Equations",
                sub_concept="Elimination",
                curriculum_stage=CurriculumStage.SHS,
                difficulty=3,
                prerequisites=["Linear Equations"],
                learning_outcomes=[
                    "Solve introductory simultaneous equations."
                ],
            ),
        ]
