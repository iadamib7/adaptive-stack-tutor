from __future__ import annotations

from collections.abc import Mapping

from backend.app.learning.adaptive_engine.models import (
    ResponseEvidence,
)


class StackEvidenceAdapter:
    """
    Convert a raw STACK grading response into the
    curriculum-independent evidence model.

    STACK remains responsible for:
    - grading;
    - PRT execution;
    - teacher-authored feedback.

    This adapter only extracts evidence for the
    adaptive question-selection engine.
    """

    def to_response_evidence(
        self,
        *,
        question_id: str,
        grade_payload: Mapping[
            str,
            object,
        ],
        outcome_aliases: Mapping[
            str,
            str,
        ] | None = None,
    ) -> ResponseEvidence:
        if not question_id.strip():
            raise ValueError(
                "question_id must not be empty."
            )

        score = self._extract_score(
            grade_payload
        )

        raw_outcome = (
            self._extract_prt_outcome(
                grade_payload
            )
        )

        semantic_outcome = (
            self._resolve_semantic_outcome(
                score=score,
                raw_outcome=raw_outcome,
                outcome_aliases=(
                    outcome_aliases
                ),
            )
        )

        return ResponseEvidence(
            question_id=question_id,
            score=score,
            prt_outcome=semantic_outcome,
        )

    @staticmethod
    def _extract_score(
        grade_payload: Mapping[
            str,
            object,
        ],
    ) -> float:
        score = grade_payload.get(
            "score"
        )

        if not isinstance(
            score,
            (int, float),
        ):
            raise ValueError(
                "STACK grading response does "
                "not contain a numeric score."
            )

        numeric_score = float(
            score
        )

        if not (
            0.0
            <= numeric_score
            <= 1.0
        ):
            raise ValueError(
                "STACK score must be "
                "between 0 and 1."
            )

        return numeric_score

    @classmethod
    def _extract_prt_outcome(
        cls,
        grade_payload: Mapping[
            str,
            object,
        ],
    ) -> str | None:
        prt_results = grade_payload.get(
            "prtresults"
        )

        if not isinstance(
            prt_results,
            Mapping,
        ):
            return None

        outcomes: list[str] = []

        for prt_name in sorted(
            str(name)
            for name
            in prt_results.keys()
        ):
            result = prt_results.get(
                prt_name
            )

            if not isinstance(
                result,
                Mapping,
            ):
                continue

            notes = result.get(
                "answernotes"
            )

            normalized_notes = (
                cls._normalize_answer_notes(
                    notes
                )
            )

            if not normalized_notes:
                continue

            outcomes.append(
                (
                    f"{prt_name}:"
                    + "|".join(
                        normalized_notes
                    )
                )
            )

        if not outcomes:
            return None

        return ";".join(
            outcomes
        )

    @staticmethod
    def _normalize_answer_notes(
        notes: object,
    ) -> list[str]:
        if isinstance(
            notes,
            str,
        ):
            pieces = notes.split(
                "|"
            )

            return [
                piece.strip()
                for piece in pieces
                if piece.strip()
            ]

        if isinstance(
            notes,
            (
                list,
                tuple,
            ),
        ):
            normalized: list[str] = []

            for note in notes:
                if not isinstance(
                    note,
                    str,
                ):
                    continue

                for piece in note.split(
                    "|"
                ):
                    cleaned = (
                        piece.strip()
                    )

                    if cleaned:
                        normalized.append(
                            cleaned
                        )

            return normalized

        return []

    @staticmethod
    def _resolve_semantic_outcome(
        *,
        score: float,
        raw_outcome: str | None,
        outcome_aliases: Mapping[
            str,
            str,
        ] | None,
    ) -> str:
        if (
            raw_outcome is not None
            and outcome_aliases is not None
        ):
            alias = outcome_aliases.get(
                raw_outcome
            )

            if alias is not None:
                return alias

        if raw_outcome is not None:
            return raw_outcome

        if score >= 1.0:
            return "correct"

        if score > 0.0:
            return "partial"

        return "incorrect"
