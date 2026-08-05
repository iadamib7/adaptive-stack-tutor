from collections import defaultdict

from backend.app.learning.concept_evidence.models import (
    ConceptEvidenceEvent,
)


class ConceptEvidenceRepository:
    """
    In-memory evidence repository for the first implementation.

    A persistent database implementation can later replace this
    class without changing the tracker interface.
    """

    def __init__(self) -> None:
        self._events: dict[
            tuple[int, str],
            list[ConceptEvidenceEvent],
        ] = defaultdict(list)

    def save(
        self,
        event: ConceptEvidenceEvent,
    ) -> None:
        key = (
            event.student_id,
            event.concept_id,
        )

        self._events[key].append(event)

    def get_events(
        self,
        student_id: int,
        concept_id: str,
    ) -> list[ConceptEvidenceEvent]:
        return self._events[
            (
                student_id,
                concept_id,
            )
        ].copy()

    def get_student_events(
        self,
        student_id: int,
    ) -> list[ConceptEvidenceEvent]:
        events: list[ConceptEvidenceEvent] = []

        for (
            stored_student_id,
            _,
        ), concept_events in self._events.items():
            if stored_student_id == student_id:
                events.extend(concept_events)

        return events
