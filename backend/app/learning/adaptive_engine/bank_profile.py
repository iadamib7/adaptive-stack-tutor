from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from xml.etree import ElementTree as ET


@dataclass(frozen=True)
class StackPRTBranchProfile:
    """
    One observable branch from an instructor-authored
    STACK potential response tree.

    Feedback is preserved as instructor evidence.
    No misconception meaning is invented here.
    """

    prt_name: str
    node_name: str

    answer_test: str

    true_answer_note: str
    false_answer_note: str

    true_feedback: str
    false_feedback: str


@dataclass(frozen=True)
class StackQuestionProfile:
    """
    Structural profile for one STACK question.

    category_path is local to the uploaded question
    bank. It is not treated as curriculum metadata.
    """

    question_id: str
    title: str

    category_path: str | None

    input_names: tuple[str, ...]
    prt_names: tuple[str, ...]

    prt_node_count: int

    branches: tuple[
        StackPRTBranchProfile,
        ...,
    ]

    deployed_seed_count: int

    # Plain-text version of the instructor-authored
    # question prompt. This is preserved only for
    # bank-local structural/content analysis.
    prompt_text: str = ""

    @property
    def has_diagnostic_feedback(
        self,
    ) -> bool:
        return any(
            branch.true_feedback
            or branch.false_feedback
            for branch in self.branches
        )


@dataclass(frozen=True)
class StackBankProfile:
    questions: tuple[
        StackQuestionProfile,
        ...,
    ]

    @property
    def count(self) -> int:
        return len(
            self.questions
        )

    def require(
        self,
        question_id: str,
    ) -> StackQuestionProfile:
        for question in self.questions:
            if (
                question.question_id
                == question_id
            ):
                return question

        raise ValueError(
            "Unknown profiled question: "
            f"{question_id}"
        )


class StackBankProfiler:
    """
    Extract trustworthy structural evidence from
    instructor-authored Moodle/STACK XML.

    The profiler does not create adaptive edges,
    prerequisites, skill labels, or misconception
    labels. Those are separate inference/policy
    concerns.
    """

    def profile_text(
        self,
        xml_text: str,
    ) -> StackBankProfile:
        if not xml_text.strip():
            raise ValueError(
                "Question-bank XML "
                "must not be empty."
            )

        root = ET.fromstring(
            xml_text
        )

        if root.tag != "quiz":
            raise ValueError(
                "Expected Moodle quiz XML "
                "with a <quiz> root."
            )

        current_category: (
            str | None
        ) = None

        profiles: list[
            StackQuestionProfile
        ] = []

        # Moodle category records affect the STACK
        # questions that follow them, so we preserve
        # document traversal only for discovering the
        # current category. This does NOT define the
        # adaptive question sequence.
        for element in root.findall(
            "question"
        ):
            question_type = (
                element.attrib.get(
                    "type"
                )
            )

            if question_type == "category":
                category = self._text_at(
                    element,
                    "category/text",
                )

                current_category = (
                    category or None
                )

                continue

            if question_type != "stack":
                continue

            profiles.append(
                self._profile_question(
                    element,
                    category_path=(
                        current_category
                    ),
                )
            )

        if not profiles:
            raise ValueError(
                "No STACK questions found "
                "in uploaded question bank."
            )

        return StackBankProfile(
            questions=tuple(
                profiles
            )
        )

    def _profile_question(
        self,
        question: ET.Element,
        *,
        category_path: (
            str | None
        ),
    ) -> StackQuestionProfile:
        stack_xml = self._wrap_question(
            question
        )

        explicit_id = self._text_at(
            question,
            "idnumber",
        )

        question_id = (
            explicit_id
            if explicit_id
            else self._stable_id(
                stack_xml
            )
        )

        title = self._text_at(
            question,
            "name/text",
        )

        if not title:
            title = question_id

        prompt_text = self._content_text(
            question,
            "questiontext/text",
        )

        input_names = tuple(
            self._text_at(
                input_element,
                "name",
            )
            for input_element
            in question.findall(
                "input"
            )
            if self._text_at(
                input_element,
                "name",
            )
        )

        prt_names: list[str] = []

        branches: list[
            StackPRTBranchProfile
        ] = []

        prt_node_count = 0

        for prt in question.findall(
            "prt"
        ):
            prt_name = self._text_at(
                prt,
                "name",
            )

            if prt_name:
                prt_names.append(
                    prt_name
                )

            for node in prt.findall(
                "node"
            ):
                prt_node_count += 1

                branches.append(
                    StackPRTBranchProfile(
                        prt_name=(
                            prt_name
                        ),
                        node_name=(
                            self._text_at(
                                node,
                                "name",
                            )
                        ),
                        answer_test=(
                            self._text_at(
                                node,
                                "answertest",
                            )
                        ),
                        true_answer_note=(
                            self._text_at(
                                node,
                                "trueanswernote",
                            )
                        ),
                        false_answer_note=(
                            self._text_at(
                                node,
                                "falseanswernote",
                            )
                        ),
                        true_feedback=(
                            self._feedback_text(
                                node,
                                "truefeedback/text",
                            )
                        ),
                        false_feedback=(
                            self._feedback_text(
                                node,
                                "falsefeedback/text",
                            )
                        ),
                    )
                )

        deployed_seed_count = len(
            [
                element
                for element
                in question.findall(
                    "deployedseed"
                )
                if (
                    element.text
                    and element.text.strip()
                )
            ]
        )

        return StackQuestionProfile(
            question_id=question_id,
            title=title,
            category_path=(
                category_path
            ),
            input_names=input_names,
            prt_names=tuple(
                prt_names
            ),
            prt_node_count=(
                prt_node_count
            ),
            branches=tuple(
                branches
            ),
            deployed_seed_count=(
                deployed_seed_count
            ),
            prompt_text=prompt_text,
        )

    @staticmethod
    def _content_text(
        element: ET.Element,
        path: str,
    ) -> str:
        raw = StackBankProfiler._text_at(
            element,
            path,
        )

        if not raw:
            return ""

        # Remove HTML while preserving the authored
        # mathematical wording.
        without_tags = re.sub(
            r"<[^>]+>",
            " ",
            raw,
        )

        # Remove STACK input/feedback placeholders
        # because ans1/prt1 etc. are not meaningful
        # content-relevance evidence.
        without_placeholders = re.sub(
            r"\[\[(?:input|validation|feedback):"
            r"[^\]]+\]\]",
            " ",
            without_tags,
            flags=re.IGNORECASE,
        )

        # Remove STACK variable interpolation syntax.
        without_variables = re.sub(
            r"\{@[^@]+@\}",
            " ",
            without_placeholders,
        )

        return " ".join(
            without_variables.split()
        )

    @staticmethod
    def _feedback_text(
        element: ET.Element,
        path: str,
    ) -> str:
        raw = StackBankProfiler._text_at(
            element,
            path,
        )

        if not raw:
            return ""

        # Preserve the instructor's wording while
        # removing HTML markup for structural
        # analysis.
        without_tags = re.sub(
            r"<[^>]+>",
            " ",
            raw,
        )

        return " ".join(
            without_tags.split()
        )

    @staticmethod
    def _text_at(
        element: ET.Element,
        path: str,
    ) -> str:
        child = element.find(
            path
        )

        if (
            child is None
            or child.text is None
        ):
            return ""

        return child.text.strip()

    @staticmethod
    def _stable_id(
        xml_text: str,
    ) -> str:
        digest = sha256(
            xml_text.encode(
                "utf-8"
            )
        ).hexdigest()[:16]

        return (
            f"stack-{digest}"
        )

    @staticmethod
    def _wrap_question(
        question: ET.Element,
    ) -> str:
        quiz = ET.Element(
            "quiz"
        )

        copied_question = (
            ET.fromstring(
                ET.tostring(
                    question,
                    encoding="unicode",
                )
            )
        )

        quiz.append(
            copied_question
        )

        return ET.tostring(
            quiz,
            encoding="unicode",
        )
