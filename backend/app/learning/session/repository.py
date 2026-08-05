from backend.app.learning.session.models import (
    LearningSessionState,
)


class LearningSessionRepository:
    """
    In-memory session repository for the first implementation.

    This can later be replaced by a database-backed repository
    without changing the session engine interface.
    """

    def __init__(self) -> None:
        self._sessions: dict[
            int,
            LearningSessionState,
        ] = {}

    def save(
        self,
        session: LearningSessionState,
    ) -> None:
        self._sessions[session.student_id] = session

    def get(
        self,
        student_id: int,
    ) -> LearningSessionState | None:
        return self._sessions.get(student_id)
