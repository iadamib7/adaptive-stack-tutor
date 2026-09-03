from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AdaptiveQuestion:
    """
    Curriculum-independent representation of one
    instructor-provided assessment question.
    """

    question_id: str
    title: str

    difficulty: float = 0.0

    tags: tuple[str, ...] = field(
        default_factory=tuple
    )

    supports: tuple[str, ...] = field(
        default_factory=tuple
    )

    diagnoses: tuple[str, ...] = field(
        default_factory=tuple
    )

    active: bool = True

    def __post_init__(self) -> None:
        if not self.question_id.strip():
            raise ValueError(
                "question_id must not be empty."
            )

        if not self.title.strip():
            raise ValueError(
                "title must not be empty."
            )


@dataclass(frozen=True)
class ResponseEvidence:
    """
    Evidence produced after one learner response.

    prt_outcome is intentionally generic. It can
    later contain a STACK PRT branch or another
    instructor-defined response classification.
    """

    question_id: str
    score: float

    prt_outcome: str | None = None

    def __post_init__(self) -> None:
        if not self.question_id.strip():
            raise ValueError(
                "question_id must not be empty."
            )

        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "score must be between 0 and 1."
            )


@dataclass
class AdaptiveLearnerState:
    """
    Curriculum-independent learner state.
    """

    learner_id: int

    ability: float = 0.0

    seen_question_ids: set[str] = field(
        default_factory=set
    )

    attempts_by_question: dict[
        str,
        int,
    ] = field(
        default_factory=dict
    )

    misconception_counts: dict[
        str,
        int,
    ] = field(
        default_factory=dict
    )

    response_history: list[
        ResponseEvidence
    ] = field(
        default_factory=list
    )

    def record(
        self,
        evidence: ResponseEvidence,
    ) -> None:
        self.response_history.append(
            evidence
        )

        self.seen_question_ids.add(
            evidence.question_id
        )

        self.attempts_by_question[
            evidence.question_id
        ] = (
            self.attempts_by_question.get(
                evidence.question_id,
                0,
            )
            + 1
        )

        if (
            evidence.prt_outcome
            and evidence.score < 1.0
        ):
            key = evidence.prt_outcome

            self.misconception_counts[
                key
            ] = (
                self.misconception_counts.get(
                    key,
                    0,
                )
                + 1
            )

        self._update_ability(
            evidence.score
        )

    def _update_ability(
        self,
        score: float,
    ) -> None:
        """
        Deliberately simple cold-start estimator.

        This is not presented as calibrated IRT.
        It provides a deterministic difficulty
        signal until a statistical model is
        available.
        """

        delta = (
            score - 0.5
        ) * 0.4

        self.ability = max(
            -3.0,
            min(
                3.0,
                self.ability + delta,
            ),
        )


@dataclass(frozen=True)
class CandidateScore:
    question_id: str

    total: float

    difficulty_match: float

    diagnostic_match: float

    novelty_bonus: float

    repetition_penalty: float


@dataclass(frozen=True)
class AdaptiveDecision:
    question: AdaptiveQuestion

    score: CandidateScore

    reason: str
