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

    # Bank-local adaptive structure.
    #
    # These are not curriculum standards.
    # They describe relationships only within
    # the instructor's uploaded question bank.
    entry_point: bool = False

    skills: tuple[str, ...] = field(
        default_factory=tuple
    )

    prerequisites: tuple[str, ...] = field(
        default_factory=tuple
    )

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
    contain a STACK PRT branch or another
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

    The remediation fields support a deterministic
    remediation -> reassessment cycle.

    Example:

        Q1 incorrect
        -> support question Q2
        -> Q2 correct
        -> reassess Q1
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

    mastered_skills: set[str] = field(
        default_factory=set
    )

    response_history: list[
        ResponseEvidence
    ] = field(
        default_factory=list
    )

    remediation_return_question_id: (
        str | None
    ) = None

    remediation_question_id: (
        str | None
    ) = None

    def record(
        self,
        evidence: ResponseEvidence,
        question: AdaptiveQuestion | None = None,
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

        if (
            question is not None
            and evidence.score >= 1.0
        ):
            self.mastered_skills.update(
                question.skills
            )

        self._update_ability(
            evidence.score
        )

    def begin_remediation(
        self,
        *,
        return_question_id: str,
        remediation_question_id: str,
    ) -> None:
        self.remediation_return_question_id = (
            return_question_id
        )

        self.remediation_question_id = (
            remediation_question_id
        )

    def update_remediation_question(
        self,
        question_id: str,
    ) -> None:
        if (
            self.remediation_return_question_id
            is None
        ):
            return

        self.remediation_question_id = (
            question_id
        )

    def clear_remediation(
        self,
    ) -> None:
        self.remediation_return_question_id = (
            None
        )

        self.remediation_question_id = None

    @property
    def in_remediation(
        self,
    ) -> bool:
        return (
            self.remediation_return_question_id
            is not None
            and self.remediation_question_id
            is not None
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

    # start:
    # first question in a session
    #
    # advance:
    # normal adaptive progression
    #
    # remediate:
    # diagnostic evidence caused a support
    # question to be selected
    #
    # reassess:
    # learner completed remediation and is
    # returned to the earlier question
    decision_type: str = "advance"

    return_target_question_id: (
        str | None
    ) = None
