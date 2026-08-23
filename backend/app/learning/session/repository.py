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
        self._sessions[
            session.student_id
        ] = session

    def get(
        self,
        student_id: int,
    ) -> LearningSessionState | None:
        return self._sessions.get(
            student_id
        )

    def delete(
        self,
        student_id: int,
    ) -> None:
        self._sessions.pop(
            student_id,
            None,
        )

    def snapshot(
        self,
        student_id: int,
    ) -> LearningSessionState | None:
        state = self.get(
            student_id
        )

        if state is None:
            return None

        return state.model_copy(
            deep=True
        )

    def restore(
        self,
        student_id: int,
        state: LearningSessionState | None,
    ) -> None:
        if state is None:
            self.delete(
                student_id
            )
            return

        self.save(
            state.model_copy(
                deep=True
            )
        )
