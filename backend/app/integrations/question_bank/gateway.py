from typing import Protocol

from backend.app.integrations.question_bank.models import (
    CurriculumStage,
    QuestionMetadata,
)


class QuestionBankGateway(Protocol):
    def get_question(
        self,
        question_id: str,
    ) -> QuestionMetadata | None:
        """Return one question or None when it does not exist."""
        ...

    def find_questions(
        self,
        *,
        concept: str | None = None,
        topic: str | None = None,
        difficulty: int | None = None,
        curriculum_stage: CurriculumStage | None = None,
    ) -> list[QuestionMetadata]:
        """Return questions matching the supplied metadata."""
        ...
