from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import re

from backend.app.learning.adaptive_engine.bank_profile import (
    StackBankProfile,
    StackQuestionProfile,
)

from backend.app.learning.adaptive_engine.models import (
    AdaptiveQuestion,
)

from backend.app.learning.adaptive_engine.question_bank import (
    AdaptiveQuestionBank,
    ImportedAdaptiveQuestion,
)


@dataclass(frozen=True)
class AdaptiveGraphBuildResult:
    """
    Result of converting a profiled instructor bank
    into a bank-local adaptive structure.

    This contains no curriculum or national-standard
    assumptions.
    """

    bank: AdaptiveQuestionBank

    entry_question_id: str

    category_skills: dict[
        str,
        str,
    ]

    outcome_aliases: dict[
        str,
        dict[str, str],
    ]


class StackAdaptiveGraphBuilder:
    """
    Build conservative adaptive structure from an
    instructor's uploaded STACK bank.

    Important:
    - XML position is never used as sequencing.
    - Categories are bank-local grouping evidence.
    - Structural complexity is only a cold-start
      difficulty heuristic.
    - No misconception labels are invented.
    """

    def build(
        self,
        *,
        bank: AdaptiveQuestionBank,
        profile: StackBankProfile,
    ) -> AdaptiveGraphBuildResult:
        bank_ids = {
            question.question_id
            for question
            in bank.adaptive_questions()
        }

        profile_ids = {
            question.question_id
            for question
            in profile.questions
        }

        if bank_ids != profile_ids:
            missing_from_profile = sorted(
                bank_ids - profile_ids
            )

            missing_from_bank = sorted(
                profile_ids - bank_ids
            )

            raise ValueError(
                "Question bank and STACK profile "
                "do not describe the same "
                "questions. "
                "Missing from profile="
                f"{missing_from_profile}; "
                "missing from bank="
                f"{missing_from_bank}."
            )

        groups = self._group_by_category(
            profile
        )

        category_skills = {
            category: self._skill_id(
                category
            )
            for category in groups
        }

        category_anchors = {
            category: min(
                questions,
                key=self._ordering_key,
            )
            for (
                category,
                questions,
            ) in groups.items()
        }

        # The global entry question is selected from
        # the simplest category anchors.
        #
        # Sorting uses structural evidence, title,
        # and stable question ID -- never XML order.
        entry_profile = min(
            category_anchors.values(),
            key=self._ordering_key,
        )

        entry_question_id = (
            entry_profile.question_id
        )

        entry_category = (
            self._category_key(
                entry_profile
            )
        )

        entry_skill = category_skills[
            entry_category
        ]

        (
            automatic_supports,
            automatic_aliases,
        ) = self._diagnostic_support_edges(
            groups
        )

        inferred: dict[
            str,
            AdaptiveQuestion,
        ] = {}

        for (
            category,
            question_profiles,
        ) in groups.items():
            skill_id = (
                category_skills[
                    category
                ]
            )

            ordered = sorted(
                question_profiles,
                key=self._ordering_key,
            )

            anchor_id = (
                category_anchors[
                    category
                ].question_id
            )

            difficulty_by_id = (
                self._difficulty_by_rank(
                    ordered
                )
            )

            for question_profile in ordered:
                imported = bank.require(
                    question_profile.question_id
                )

                current = (
                    imported.adaptive_question
                )

                if (
                    question_profile.question_id
                    == entry_question_id
                ):
                    prerequisites: (
                        tuple[str, ...]
                    ) = ()

                    entry_point = True

                elif (
                    question_profile.question_id
                    == anchor_id
                ):
                    # The simplest question in a new
                    # category becomes available only
                    # after mastery evidence from the
                    # global entry area.
                    prerequisites = (
                        entry_skill,
                    )

                    entry_point = False

                else:
                    # More complex questions in a
                    # category unlock after mastery
                    # evidence in that bank-local area.
                    prerequisites = (
                        skill_id,
                    )

                    entry_point = False

                inferred[
                    question_profile.question_id
                ] = replace(
                    current,
                    entry_point=entry_point,
                    skills=(
                        skill_id,
                    ),
                    prerequisites=(
                        prerequisites
                    ),
                    difficulty=(
                        difficulty_by_id[
                            question_profile
                            .question_id
                        ]
                    ),

                    # Preserve instructor metadata and
                    # add conservative support keys derived
                    # from instructor-authored PRT feedback.
                    tags=current.tags,
                    supports=tuple(
                        dict.fromkeys(
                            (
                                *current.supports,
                                *sorted(
                                    automatic_supports
                                    .get(
                                        question_profile
                                        .question_id,
                                        set(),
                                    )
                                ),
                            )
                        )
                    ),
                    diagnoses=current.diagnoses,
                )

        updated: list[
            ImportedAdaptiveQuestion
        ] = []

        # Preserve the bank's storage representation.
        # Routing decisions do not depend on this
        # iteration order.
        for question in (
            bank.adaptive_questions()
        ):
            imported = bank.require(
                question.question_id
            )

            updated.append(
                ImportedAdaptiveQuestion(
                    adaptive_question=(
                        inferred[
                            question.question_id
                        ]
                    ),
                    stack_xml=(
                        imported.stack_xml
                    ),
                )
            )

        return AdaptiveGraphBuildResult(
            bank=AdaptiveQuestionBank(
                updated
            ),
            entry_question_id=(
                entry_question_id
            ),
            category_skills=(
                category_skills
            ),
            outcome_aliases=(
                automatic_aliases
            ),
        )

    @classmethod
    def _diagnostic_support_edges(
        cls,
        groups: dict[
            str,
            list[StackQuestionProfile],
        ],
    ) -> tuple[
        dict[str, set[str]],
        dict[str, dict[str, str]],
    ]:
        """
        Create conservative remediation links from
        instructor-authored STACK feedback branches.

        No misconception label is invented.

        A feedback-bearing answer note receives a
        stable internal support key. A structurally
        simpler question from the same bank-local
        category may support that key.
        """

        supports: dict[
            str,
            set[str],
        ] = {}

        aliases: dict[
            str,
            dict[str, str],
        ] = {}

        for question_profiles in (
            groups.values()
        ):
            ordered = sorted(
                question_profiles,
                key=cls._ordering_key,
            )

            for source in ordered:
                support_question = (
                    cls._support_candidate(
                        source=source,
                        questions=ordered,
                    )
                )

                if support_question is None:
                    continue

                for branch in source.branches:
                    feedback_outcomes: list[
                        tuple[
                            str,
                            str,
                        ]
                    ] = []

                    if (
                        branch.true_feedback
                        and branch.true_answer_note
                    ):
                        feedback_outcomes.append(
                            (
                                "true",
                                branch.true_answer_note,
                            )
                        )

                    if (
                        branch.false_feedback
                        and branch.false_answer_note
                    ):
                        feedback_outcomes.append(
                            (
                                "false",
                                branch.false_answer_note,
                            )
                        )

                    for (
                        side,
                        answer_note,
                    ) in feedback_outcomes:
                        support_key = (
                            cls._support_key(
                                source=source,
                                prt_name=(
                                    branch.prt_name
                                ),
                                node_name=(
                                    branch.node_name
                                ),
                                side=side,
                                answer_note=(
                                    answer_note
                                ),
                            )
                        )

                        supports.setdefault(
                            support_question.question_id,
                            set(),
                        ).add(
                            support_key
                        )

                        aliases.setdefault(
                            source.question_id,
                            {},
                        )[
                            "note:"
                            + answer_note
                        ] = support_key

        return (
            supports,
            aliases,
        )

    @classmethod
    def _support_candidate(
        cls,
        *,
        source: StackQuestionProfile,
        questions: list[
            StackQuestionProfile
        ],
    ) -> StackQuestionProfile | None:
        """
        Select a conservative support question.

        A candidate must:
        1. be structurally simpler,
        2. already belong to the same bank-local
           category supplied to this method,
        3. share meaningful mathematical vocabulary
           with the source.

        If content relevance is too weak, no
        remediation edge is created.
        """

        source_complexity = (
            cls._complexity(
                source
            )
        )

        candidates = [
            question
            for question in questions
            if (
                question.question_id
                != source.question_id
                and cls._complexity(
                    question
                )
                < source_complexity
            )
        ]

        if not candidates:
            return None

        scored = [
            (
                cls._content_relevance(
                    source=source,
                    candidate=question,
                ),
                question,
            )
            for question in candidates
        ]

        relevant = [
            (
                score,
                question,
            )
            for (
                score,
                question,
            ) in scored
            if score >= 1.0
        ]

        if not relevant:
            return None

        # Higher content relevance wins first.
        # If tied, prefer the structurally closest
        # simpler question. Final title/ID sorting
        # keeps the result deterministic.
        return max(
            relevant,
            key=lambda item: (
                item[0],
                cls._complexity(
                    item[1]
                ),
                item[1].title.casefold(),
                item[1].question_id,
            ),
        )[1]

    @classmethod
    def _content_relevance(
        cls,
        *,
        source: StackQuestionProfile,
        candidate: StackQuestionProfile,
    ) -> float:
        """
        Lexical cold-start relevance.

        This is intentionally transparent and
        conservative. It is not a semantic model and
        does not claim to infer mathematical
        prerequisites or misconceptions.
        """

        source_title = cls._content_terms(
            source.title
        )

        candidate_title = cls._content_terms(
            candidate.title
        )

        source_prompt = cls._content_terms(
            source.prompt_text
        )

        candidate_prompt = cls._content_terms(
            candidate.prompt_text
        )

        title_overlap = (
            source_title
            & candidate_title
        )

        # Automatic remediation requires at least
        # one meaningful topic term shared by the
        # question titles.
        #
        # Prompt overlap alone is too weak because
        # unrelated mathematics questions often use
        # similar instructional language.
        if not title_overlap:
            return 0.0

        all_source = (
            source_title
            | source_prompt
        )

        all_candidate = (
            candidate_title
            | candidate_prompt
        )

        overall_overlap = (
            all_source
            & all_candidate
        )

        # Title agreement establishes topical
        # relevance. Prompt agreement only refines
        # the ranking among already-related items.
        return (
            2.0
            * float(
                len(
                    title_overlap
                )
            )
            + 0.25
            * float(
                len(
                    overall_overlap
                    - title_overlap
                )
            )
        )

    @staticmethod
    def _content_terms(
        text: str,
    ) -> set[str]:
        """
        Extract meaningful bank-local vocabulary.

        Common assessment verbs and generic math
        words are removed so words like 'solve' or
        'equation' cannot create a support edge by
        themselves.
        """

        stopwords = {
            "a",
            "an",
            "and",
            "answer",
            "answers",
            "at",
            "be",
            "by",
            "calculate",
            "check",
            "determine",
            "equation",
            "equations",
            "example",
            "examples",
            "expression",
            "expressions",
            "find",
            "for",
            "form",
            "from",
            "function",
            "functions",
            "give",
            "given",
            "graph",
            "graphs",
            "identify",
            "in",
            "is",
            "of",
            "on",
            "one",
            "problem",
            "problems",
            "question",
            "questions",
            "show",
            "simplify",
            "solve",
            "solving",
            "that",
            "the",
            "to",
            "using",
            "value",
            "values",
            "with",
            "write",
        }

        tokens = re.findall(
            r"[A-Za-z][A-Za-z0-9_-]*",
            text.casefold(),
        )

        result: set[str] = set()

        for token in tokens:
            cleaned = token.strip(
                "_-"
            )

            if (
                len(cleaned) < 3
                or cleaned in stopwords
            ):
                continue

            # Very small normalization for ordinary
            # plurals only. Avoid aggressive stemming
            # that could distort mathematical terms.
            if (
                len(cleaned) > 4
                and cleaned.endswith("s")
                and not cleaned.endswith(
                    "ss"
                )
            ):
                cleaned = cleaned[:-1]

            result.add(
                cleaned
            )

        return result

    @staticmethod
    def _support_key(
        *,
        source: StackQuestionProfile,
        prt_name: str,
        node_name: str,
        side: str,
        answer_note: str,
    ) -> str:
        raw = (
            source.question_id
            + "|"
            + prt_name
            + "|"
            + node_name
            + "|"
            + side
            + "|"
            + answer_note
        )

        digest = sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()[:16]

        return (
            f"bank-support-{digest}"
        )

    @staticmethod
    def _group_by_category(
        profile: StackBankProfile,
    ) -> dict[
        str,
        list[StackQuestionProfile],
    ]:
        groups: dict[
            str,
            list[StackQuestionProfile],
        ] = {}

        for question in profile.questions:
            category = (
                StackAdaptiveGraphBuilder
                ._category_key(
                    question
                )
            )

            groups.setdefault(
                category,
                [],
            ).append(
                question
            )

        return groups

    @staticmethod
    def _category_key(
        question: StackQuestionProfile,
    ) -> str:
        raw = (
            question.category_path
            or "__uncategorized__"
        )

        normalized = " ".join(
            raw.split()
        )

        return (
            normalized
            or "__uncategorized__"
        )

    @staticmethod
    def _skill_id(
        category: str,
    ) -> str:
        digest = sha256(
            category.encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        return (
            f"bank-skill-{digest}"
        )

    @staticmethod
    def _complexity(
        question: StackQuestionProfile,
    ) -> float:
        """
        Cold-start structural complexity.

        This is NOT empirical item difficulty and
        is NOT presented as IRT difficulty.
        """

        return (
            float(
                len(
                    question.input_names
                )
            )
            + (
                0.5
                * float(
                    question.prt_node_count
                )
            )
        )

    @classmethod
    def _ordering_key(
        cls,
        question: StackQuestionProfile,
    ) -> tuple[
        float,
        str,
        str,
    ]:
        return (
            cls._complexity(
                question
            ),
            question.title.casefold(),
            question.question_id,
        )

    @classmethod
    def _difficulty_by_rank(
        cls,
        questions: list[
            StackQuestionProfile
        ],
    ) -> dict[
        str,
        float,
    ]:
        if len(questions) == 1:
            return {
                questions[
                    0
                ].question_id: 0.0
            }

        result: dict[
            str,
            float,
        ] = {}

        count = len(
            questions
        )

        # Spread cold-start question difficulty over
        # [-0.8, 0.8] within a bank-local category.
        for index, question in enumerate(
            questions
        ):
            position = (
                float(index)
                / float(
                    count - 1
                )
            )

            difficulty = (
                -0.8
                + (
                    1.6
                    * position
                )
            )

            result[
                question.question_id
            ] = round(
                difficulty,
                6,
            )

        return result
