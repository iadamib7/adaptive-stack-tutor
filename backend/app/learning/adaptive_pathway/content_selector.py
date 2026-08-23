from backend.app.content.models import (
    LearningContentItem,
)
from backend.app.content.repository import (
    LearningContentRepository,
)


class AdaptiveContentSelector:
    """
    Deterministically select deliverable content.

    Unseen questions are preferred first. When repetition
    is required, the least-attempted question is selected.
    Curriculum order breaks ties.
    """

    def __init__(
        self,
        content_repository: LearningContentRepository,
    ) -> None:
        self.content_repository = content_repository

    def select_question(
        self,
        concept_id: str,
        seen_content_ids: set[str] | None = None,
        allow_repeat: bool = False,
        repeat_attempt_counts: (
            dict[str, int] | None
        ) = None,
    ) -> LearningContentItem | None:
        seen = set(
            seen_content_ids or set()
        )

        questions = (
            self.content_repository
            .questions_for_concept(
                concept_id
            )
        )

        unseen = (
            self.content_repository
            .excluding_seen(
                questions,
                seen,
            )
        )

        if unseen:
            return unseen[0]

        if not allow_repeat:
            return None

        if not questions:
            return None

        counts = (
            repeat_attempt_counts
            or {}
        )

        return min(
            questions,
            key=lambda question: (
                counts.get(
                    question.content_id,
                    0,
                ),
                questions.index(
                    question
                ),
            ),
        )
