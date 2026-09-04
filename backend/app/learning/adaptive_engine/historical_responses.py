from __future__ import annotations

import csv
import re

from collections import Counter
from dataclasses import dataclass
from io import StringIO


QUESTION_HEADER = re.compile(
    r"^Question\s+(\d+)$",
    re.IGNORECASE,
)

RESPONSE_HEADER = re.compile(
    r"^Response\s+(\d+)$",
    re.IGNORECASE,
)

RIGHT_ANSWER_HEADER = re.compile(
    r"^Right answer\s+(\d+)$",
    re.IGNORECASE,
)

SEED_PATTERN = re.compile(
    r"(?:^|;\s*)Seed:\s*(\d+)",
    re.IGNORECASE,
)

PRT_PATTERN = re.compile(
    r"(?:^|;\s*)"
    r"(prt[^:;]+):\s*"
    r"#\s*=\s*"
    r"([-+]?\d*\.?\d+)"
    r"(.*?)(?=;\s*prt[^:;]+:|$)",
    re.IGNORECASE,
)

ANSWER_PATTERN = re.compile(
    r"(?:^|;\s*)"
    r"(ans\d+):\s*"
    r"(.*?)"
    r"\s*\[score\]"
    r"(?=;|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class HistoricalPRTResult:
    prt_name: str
    score: float
    answer_notes: tuple[str, ...]


@dataclass(frozen=True)
class HistoricalQuestionAttempt:
    """
    One learner attempt on one exported STACK
    question slot.

    No learner name or email is retained.
    """

    attempt_index: int
    question_number: int

    question_text: str

    response_text: str
    right_answer_text: str

    seed: int | None

    submitted_answers: tuple[
        tuple[str, str],
        ...,
    ]

    prts: tuple[
        HistoricalPRTResult,
        ...,
    ]

    @property
    def score(self) -> float:
        """
        Mean PRT score for this question attempt.

        This is an empirical question-attempt score,
        not an IRT ability estimate.
        """

        if not self.prts:
            return 0.0

        return sum(
            prt.score
            for prt in self.prts
        ) / len(
            self.prts
        )


@dataclass(frozen=True)
class HistoricalItemStatistics:
    question_number: int

    attempt_count: int

    mean_score: float
    full_credit_rate: float
    zero_credit_rate: float

    unique_seeds: int

    prt_outcome_counts: tuple[
        tuple[str, int],
        ...,
    ]


@dataclass(frozen=True)
class HistoricalStackDataset:
    source_name: str

    attempts: tuple[
        HistoricalQuestionAttempt,
        ...,
    ]

    item_statistics: tuple[
        HistoricalItemStatistics,
        ...,
    ]

    @property
    def question_count(self) -> int:
        return len(
            self.item_statistics
        )

    @property
    def attempt_count(self) -> int:
        return len(
            {
                attempt.attempt_index
                for attempt
                in self.attempts
            }
        )


class HistoricalStackResponseImporter:
    """
    Parse Moodle/STACK response-export CSV files.

    Expected repeated columns look like:

        Question 1
        Response 1
        Right answer 1
        Question 2
        Response 2
        Right answer 2
        ...

    This parser intentionally does not retain
    learner names or email addresses.
    """

    def import_bytes(
        self,
        *,
        filename: str,
        content: bytes,
    ) -> HistoricalStackDataset:
        try:
            text = content.decode(
                "utf-8-sig"
            )
        except UnicodeDecodeError as error:
            raise ValueError(
                "STACK response CSV must "
                "be UTF-8 encoded."
            ) from error

        return self.import_text(
            source_name=filename,
            csv_text=text,
        )

    def import_text(
        self,
        *,
        source_name: str,
        csv_text: str,
    ) -> HistoricalStackDataset:
        reader = csv.DictReader(
            StringIO(
                csv_text
            )
        )

        if reader.fieldnames is None:
            raise ValueError(
                "STACK response CSV "
                "does not contain headers."
            )

        question_columns = (
            self._discover_question_columns(
                reader.fieldnames
            )
        )

        if not question_columns:
            raise ValueError(
                "CSV does not look like a "
                "STACK response export. "
                "Expected columns such as "
                "'Question 1', 'Response 1', "
                "and 'Right answer 1'."
            )

        attempts: list[
            HistoricalQuestionAttempt
        ] = []

        for attempt_index, row in enumerate(
            reader,
            start=1,
        ):
            for (
                question_number,
                columns,
            ) in question_columns.items():
                question_text = (
                    row.get(
                        columns[
                            "question"
                        ],
                        "",
                    )
                    or ""
                ).strip()

                response_text = (
                    row.get(
                        columns[
                            "response"
                        ],
                        "",
                    )
                    or ""
                ).strip()

                right_answer_text = (
                    row.get(
                        columns[
                            "right_answer"
                        ],
                        "",
                    )
                    or ""
                ).strip()

                if not (
                    question_text
                    or response_text
                    or right_answer_text
                ):
                    continue

                attempts.append(
                    HistoricalQuestionAttempt(
                        attempt_index=(
                            attempt_index
                        ),
                        question_number=(
                            question_number
                        ),
                        question_text=(
                            question_text
                        ),
                        response_text=(
                            response_text
                        ),
                        right_answer_text=(
                            right_answer_text
                        ),
                        seed=self._extract_seed(
                            response_text
                        ),
                        submitted_answers=(
                            self._extract_answers(
                                response_text
                            )
                        ),
                        prts=self._extract_prts(
                            response_text
                        ),
                    )
                )

        if not attempts:
            raise ValueError(
                "No historical STACK "
                "question attempts were found."
            )

        statistics = (
            self._build_statistics(
                attempts
            )
        )

        return HistoricalStackDataset(
            source_name=source_name,
            attempts=tuple(
                attempts
            ),
            item_statistics=tuple(
                statistics
            ),
        )

    @staticmethod
    def _discover_question_columns(
        headers: list[str],
    ) -> dict[
        int,
        dict[str, str],
    ]:
        discovered: dict[
            int,
            dict[str, str],
        ] = {}

        for header in headers:
            cleaned = header.strip()

            question_match = (
                QUESTION_HEADER.match(
                    cleaned
                )
            )

            response_match = (
                RESPONSE_HEADER.match(
                    cleaned
                )
            )

            right_match = (
                RIGHT_ANSWER_HEADER.match(
                    cleaned
                )
            )

            if question_match:
                number = int(
                    question_match.group(
                        1
                    )
                )

                discovered.setdefault(
                    number,
                    {},
                )[
                    "question"
                ] = header

            elif response_match:
                number = int(
                    response_match.group(
                        1
                    )
                )

                discovered.setdefault(
                    number,
                    {},
                )[
                    "response"
                ] = header

            elif right_match:
                number = int(
                    right_match.group(
                        1
                    )
                )

                discovered.setdefault(
                    number,
                    {},
                )[
                    "right_answer"
                ] = header

        complete: dict[
            int,
            dict[str, str],
        ] = {}

        required = {
            "question",
            "response",
            "right_answer",
        }

        for (
            number,
            columns,
        ) in discovered.items():
            if required.issubset(
                columns
            ):
                complete[
                    number
                ] = columns

        return dict(
            sorted(
                complete.items()
            )
        )

    @staticmethod
    def _extract_seed(
        response_text: str,
    ) -> int | None:
        match = SEED_PATTERN.search(
            response_text
        )

        if match is None:
            return None

        return int(
            match.group(
                1
            )
        )

    @staticmethod
    def _extract_answers(
        response_text: str,
    ) -> tuple[
        tuple[str, str],
        ...,
    ]:
        answers = [
            (
                match.group(1),
                match.group(2).strip(),
            )
            for match
            in ANSWER_PATTERN.finditer(
                response_text
            )
        ]

        return tuple(
            answers
        )

    @staticmethod
    def _extract_prts(
        response_text: str,
    ) -> tuple[
        HistoricalPRTResult,
        ...,
    ]:
        results: list[
            HistoricalPRTResult
        ] = []

        for match in PRT_PATTERN.finditer(
            response_text
        ):
            prt_name = (
                match.group(1)
                .strip()
            )

            score = float(
                match.group(2)
            )

            raw_notes = (
                match.group(3)
                .strip()
            )

            if raw_notes.startswith(
                "|"
            ):
                raw_notes = (
                    raw_notes[1:]
                    .strip()
                )

            notes = tuple(
                part.strip()
                for part
                in raw_notes.split("|")
                if part.strip()
            )

            results.append(
                HistoricalPRTResult(
                    prt_name=prt_name,
                    score=score,
                    answer_notes=notes,
                )
            )

        return tuple(
            results
        )

    @staticmethod
    def _build_statistics(
        attempts: list[
            HistoricalQuestionAttempt
        ],
    ) -> list[
        HistoricalItemStatistics
    ]:
        grouped: dict[
            int,
            list[
                HistoricalQuestionAttempt
            ],
        ] = {}

        for attempt in attempts:
            grouped.setdefault(
                attempt.question_number,
                [],
            ).append(
                attempt
            )

        statistics: list[
            HistoricalItemStatistics
        ] = []

        for (
            question_number,
            question_attempts,
        ) in sorted(
            grouped.items()
        ):
            scores = [
                attempt.score
                for attempt
                in question_attempts
            ]

            mean_score = (
                sum(scores)
                / len(scores)
            )

            full_credit_rate = (
                sum(
                    1
                    for score
                    in scores
                    if score >= 1.0
                )
                / len(scores)
            )

            zero_credit_rate = (
                sum(
                    1
                    for score
                    in scores
                    if score <= 0.0
                )
                / len(scores)
            )

            seeds = {
                attempt.seed
                for attempt
                in question_attempts
                if attempt.seed
                is not None
            }

            outcome_counter: Counter[
                str
            ] = Counter()

            for attempt in (
                question_attempts
            ):
                for prt in attempt.prts:
                    if prt.answer_notes:
                        outcome = (
                            f"{prt.prt_name}:"
                            + "|".join(
                                prt.answer_notes
                            )
                        )
                    else:
                        outcome = (
                            f"{prt.prt_name}:"
                            f"score={prt.score:g}"
                        )

                    outcome_counter[
                        outcome
                    ] += 1

            statistics.append(
                HistoricalItemStatistics(
                    question_number=(
                        question_number
                    ),
                    attempt_count=len(
                        question_attempts
                    ),
                    mean_score=(
                        mean_score
                    ),
                    full_credit_rate=(
                        full_credit_rate
                    ),
                    zero_credit_rate=(
                        zero_credit_rate
                    ),
                    unique_seeds=len(
                        seeds
                    ),
                    prt_outcome_counts=(
                        tuple(
                            sorted(
                                outcome_counter
                                .items(),
                                key=lambda item: (
                                    -item[1],
                                    item[0],
                                ),
                            )
                        )
                    ),
                )
            )

        return statistics
