from backend.app.content.models import (
    LearningContentItem,
)
from backend.app.content.repository import (
    LearningContentRepository,
)


class AdaptiveContentSelector:
    """
    Select deliverable unseen content for a concept.
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

        if allow_repeat and questions:
            return questions[0]

        return None