from backend.app.learning.concept_mastery.models import (
    ConceptMasteryState,
)


class ConceptMasteryRepository:
    """
    In-memory mastery repository for the first implementation.

    It can later be replaced by a database-backed repository
    without changing the mastery engine interface.
    """

    def __init__(self) -> None:
        self._states: dict[
            tuple[int, str],
            ConceptMasteryState,
        ] = {}

    def save(
        self,
        state: ConceptMasteryState,
    ) -> None:
        key = (
            state.student_id,
            state.concept_id,
        )

        self._states[key] = state

    def get(
        self,
        student_id: int,
        concept_id: str,
    ) -> ConceptMasteryState | None:
        return self._states.get(
            (
                student_id,
                concept_id,
            )
        )

    def get_student_states(
        self,
        student_id: int,
    ) -> list[ConceptMasteryState]:
        return [
            state
            for (
                stored_student_id,
                _,
            ), state in self._states.items()
            if stored_student_id == student_id
        ]
