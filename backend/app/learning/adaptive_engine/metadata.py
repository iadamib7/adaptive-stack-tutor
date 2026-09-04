from __future__ import annotations

import json
from dataclasses import dataclass, replace

from backend.app.learning.adaptive_engine.question_bank import (
    AdaptiveQuestionBank,
    ImportedAdaptiveQuestion,
)


@dataclass(frozen=True)
class QuestionAdaptiveMetadata:
    """
    Optional instructor-provided adaptive metadata.

    This is question-bank metadata, not curriculum
    information.
    """

    difficulty: float | None = None

    entry_point: bool = False

    skills: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()

    tags: tuple[str, ...] = ()
    supports: tuple[str, ...] = ()
    diagnoses: tuple[str, ...] = ()

    prt_outcomes: tuple[
        tuple[str, str],
        ...,
    ] = ()


@dataclass(frozen=True)
class AdaptiveMetadataManifest:
    questions: dict[
        str,
        QuestionAdaptiveMetadata,
    ]

    def outcome_aliases(
        self,
    ) -> dict[
        str,
        dict[str, str],
    ]:
        aliases: dict[
            str,
            dict[str, str],
        ] = {}

        for (
            question_id,
            metadata,
        ) in self.questions.items():
            if not metadata.prt_outcomes:
                continue

            aliases[
                question_id
            ] = dict(
                metadata.prt_outcomes
            )

        return aliases


class AdaptiveMetadataLoader:
    """
    Load optional adaptive metadata supplied
    alongside an instructor's STACK question bank.
    """

    def load_text(
        self,
        json_text: str,
    ) -> AdaptiveMetadataManifest:
        if not json_text.strip():
            raise ValueError(
                "Adaptive metadata JSON "
                "must not be empty."
            )

        try:
            payload = json.loads(
                json_text
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                "Adaptive metadata is not "
                "valid JSON."
            ) from error

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "Adaptive metadata root "
                "must be an object."
            )

        raw_questions = payload.get(
            "questions",
            {},
        )

        if not isinstance(
            raw_questions,
            dict,
        ):
            raise ValueError(
                "'questions' must be "
                "a JSON object."
            )

        questions: dict[
            str,
            QuestionAdaptiveMetadata,
        ] = {}

        for (
            question_id,
            raw_metadata,
        ) in raw_questions.items():
            if not isinstance(
                question_id,
                str,
            ):
                raise ValueError(
                    "Question IDs must "
                    "be strings."
                )

            if not isinstance(
                raw_metadata,
                dict,
            ):
                raise ValueError(
                    "Metadata for "
                    f"{question_id} "
                    "must be an object."
                )

            questions[
                question_id
            ] = self._parse_question(
                question_id=question_id,
                payload=raw_metadata,
            )

        return AdaptiveMetadataManifest(
            questions=questions
        )

    def apply(
        self,
        *,
        bank: AdaptiveQuestionBank,
        manifest: AdaptiveMetadataManifest,
    ) -> AdaptiveQuestionBank:
        known_ids = {
            question.question_id
            for question
            in bank.adaptive_questions()
        }

        unknown_ids = (
            set(
                manifest.questions
            )
            - known_ids
        )

        if unknown_ids:
            unknown = ", ".join(
                sorted(
                    unknown_ids
                )
            )

            raise ValueError(
                "Adaptive metadata refers "
                "to unknown question IDs: "
                f"{unknown}"
            )

        updated: list[
            ImportedAdaptiveQuestion
        ] = []

        for question in (
            bank.adaptive_questions()
        ):
            imported = bank.require(
                question.question_id
            )

            metadata = (
                manifest.questions.get(
                    question.question_id
                )
            )

            if metadata is None:
                updated.append(
                    imported
                )
                continue

            difficulty = (
                metadata.difficulty
                if metadata.difficulty
                is not None
                else question.difficulty
            )

            updated_question = replace(
                question,
                difficulty=difficulty,
                entry_point=(
                    metadata.entry_point
                ),
                skills=metadata.skills,
                prerequisites=(
                    metadata.prerequisites
                ),
                tags=metadata.tags,
                supports=metadata.supports,
                diagnoses=metadata.diagnoses,
            )

            updated.append(
                ImportedAdaptiveQuestion(
                    adaptive_question=(
                        updated_question
                    ),
                    stack_xml=(
                        imported.stack_xml
                    ),
                )
            )

        return AdaptiveQuestionBank(
            updated
        )

    @staticmethod
    def _parse_question(
        *,
        question_id: str,
        payload: dict[
            str,
            object,
        ],
    ) -> QuestionAdaptiveMetadata:
        difficulty = payload.get(
            "difficulty"
        )

        if (
            difficulty is not None
            and not isinstance(
                difficulty,
                (int, float),
            )
        ):
            raise ValueError(
                "difficulty for "
                f"{question_id} "
                "must be numeric."
            )

        numeric_difficulty = (
            float(difficulty)
            if difficulty is not None
            else None
        )

        if (
            numeric_difficulty
            is not None
            and not (
                -3.0
                <= numeric_difficulty
                <= 3.0
            )
        ):
            raise ValueError(
                "difficulty for "
                f"{question_id} "
                "must be between "
                "-3 and 3."
            )

        entry_point = payload.get(
            "entry_point",
            False,
        )

        if not isinstance(
            entry_point,
            bool,
        ):
            raise ValueError(
                "entry_point for "
                f"{question_id} "
                "must be true or false."
            )

        skills = (
            AdaptiveMetadataLoader
            ._string_tuple(
                payload.get(
                    "skills",
                    [],
                ),
                field_name="skills",
                question_id=question_id,
            )
        )

        prerequisites = (
            AdaptiveMetadataLoader
            ._string_tuple(
                payload.get(
                    "prerequisites",
                    [],
                ),
                field_name="prerequisites",
                question_id=question_id,
            )
        )

        tags = (
            AdaptiveMetadataLoader
            ._string_tuple(
                payload.get(
                    "tags",
                    [],
                ),
                field_name="tags",
                question_id=question_id,
            )
        )

        supports = (
            AdaptiveMetadataLoader
            ._string_tuple(
                payload.get(
                    "supports",
                    [],
                ),
                field_name="supports",
                question_id=question_id,
            )
        )

        diagnoses = (
            AdaptiveMetadataLoader
            ._string_tuple(
                payload.get(
                    "diagnoses",
                    [],
                ),
                field_name="diagnoses",
                question_id=question_id,
            )
        )

        raw_prt = payload.get(
            "prt_outcomes",
            {},
        )

        if not isinstance(
            raw_prt,
            dict,
        ):
            raise ValueError(
                "prt_outcomes for "
                f"{question_id} "
                "must be an object."
            )

        prt_outcomes: list[
            tuple[str, str]
        ] = []

        for (
            raw_outcome,
            semantic_outcome,
        ) in raw_prt.items():
            if (
                not isinstance(
                    raw_outcome,
                    str,
                )
                or not raw_outcome.strip()
                or not isinstance(
                    semantic_outcome,
                    str,
                )
                or not semantic_outcome.strip()
            ):
                raise ValueError(
                    "PRT outcome mappings "
                    "must contain non-empty "
                    "string keys and values."
                )

            prt_outcomes.append(
                (
                    raw_outcome.strip(),
                    semantic_outcome.strip(),
                )
            )

        return QuestionAdaptiveMetadata(
            difficulty=(
                numeric_difficulty
            ),
            entry_point=entry_point,
            skills=skills,
            prerequisites=prerequisites,
            tags=tags,
            supports=supports,
            diagnoses=diagnoses,
            prt_outcomes=tuple(
                sorted(
                    prt_outcomes
                )
            ),
        )

    @staticmethod
    def _string_tuple(
        value: object,
        *,
        field_name: str,
        question_id: str,
    ) -> tuple[str, ...]:
        if not isinstance(
            value,
            list,
        ):
            raise ValueError(
                f"{field_name} for "
                f"{question_id} "
                "must be a list."
            )

        cleaned: list[str] = []

        for item in value:
            if (
                not isinstance(
                    item,
                    str,
                )
                or not item.strip()
            ):
                raise ValueError(
                    f"{field_name} for "
                    f"{question_id} "
                    "must contain only "
                    "non-empty strings."
                )

            cleaned.append(
                item.strip()
            )

        return tuple(
            cleaned
        )
