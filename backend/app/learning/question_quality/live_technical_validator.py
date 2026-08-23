from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as ET

import requests

from backend.app.learning.question_quality.models import (
    QuestionQualityReport,
)
from backend.app.learning.question_quality.technical_validator import (
    TechnicalQuestionValidator,
)


class LiveTechnicalQuestionValidator:
    """
    Run technical checks against a deployed STACK question.

    This validator checks whether the XML parses, whether
    deployed variants exist, whether STACK can render the
    question, whether grading succeeds, and whether a PRT
    result is returned.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3080",
        timeout_seconds: int = 120,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

        self.session = (
            session
            if session is not None
            else requests.Session()
        )

        self.report_builder = (
            TechnicalQuestionValidator()
        )

    def validate(
        self,
        question_id: str,
        question_xml: str,
        seed: int | None = None,
    ) -> QuestionQualityReport:
        xml_valid = self._xml_is_valid(
            question_xml
        )

        if not xml_valid:
            return self.report_builder.validate(
                question_id=question_id,
                xml_valid=False,
                deploy_successful=False,
                render_successful=False,
                grading_successful=False,
                prt_successful=False,
            )

        deployed_seeds = (
            self._get_deployed_seeds(
                question_xml
            )
        )

        deploy_successful = bool(
            deployed_seeds
        )

        if not deploy_successful:
            return self.report_builder.validate(
                question_id=question_id,
                xml_valid=True,
                deploy_successful=False,
                render_successful=False,
                grading_successful=False,
                prt_successful=False,
            )

        selected_seed = (
            seed
            if seed is not None
            else deployed_seeds[0]
        )

        render_payload = self._render(
            question_xml=question_xml,
            seed=selected_seed,
        )

        render_successful = (
            render_payload is not None
        )

        if not render_successful:
            return self.report_builder.validate(
                question_id=question_id,
                xml_valid=True,
                deploy_successful=True,
                render_successful=False,
                grading_successful=False,
                prt_successful=False,
            )

        sample_answers = (
            self._extract_sample_answers(
                render_payload
            )
        )

        if not sample_answers:
            return self.report_builder.validate(
                question_id=question_id,
                xml_valid=True,
                deploy_successful=True,
                render_successful=True,
                grading_successful=False,
                prt_successful=False,
            )

        grade_payload = self._grade(
            question_xml=question_xml,
            seed=selected_seed,
            answers=sample_answers,
        )

        grading_successful = (
            grade_payload is not None
            and bool(
                grade_payload.get(
                    "isgradable",
                    False,
                )
            )
        )

        prt_successful = (
            grading_successful
            and self._prt_executed(
                grade_payload
            )
        )

        return self.report_builder.validate(
            question_id=question_id,
            xml_valid=True,
            deploy_successful=True,
            render_successful=True,
            grading_successful=grading_successful,
            prt_successful=prt_successful,
        )

    @staticmethod
    def _xml_is_valid(
        question_xml: str,
    ) -> bool:
        try:
            ET.fromstring(question_xml)
        except ET.ParseError:
            return False

        return True

    @staticmethod
    def _get_deployed_seeds(
        question_xml: str,
    ) -> list[int]:
        try:
            root = ET.fromstring(
                question_xml
            )
        except ET.ParseError:
            return []

        seeds: list[int] = []

        for element in root.iter(
            "deployedseed"
        ):
            if (
                element.text is None
                or not element.text.strip()
            ):
                continue

            try:
                seed = int(
                    element.text.strip()
                )
            except ValueError:
                continue

            seeds.append(seed)

        return seeds

    def _render(
        self,
        question_xml: str,
        seed: int,
    ) -> dict[str, Any] | None:
        try:
            response = self.session.post(
                f"{self.base_url}/render",
                json={
                    "questionDefinition":
                        question_xml,
                    "seed": seed,
                },
                timeout=self.timeout_seconds,
            )
        except requests.RequestException:
            return None

        if not response.ok:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        if not isinstance(
            payload,
            dict,
        ):
            return None

        return payload

    def _grade(
        self,
        question_xml: str,
        seed: int,
        answers: dict[str, str],
    ) -> dict[str, Any] | None:
        try:
            response = self.session.post(
                f"{self.base_url}/grade",
                json={
                    "questionDefinition":
                        question_xml,
                    "seed": seed,
                    "answers": answers,
                },
                timeout=self.timeout_seconds,
            )
        except requests.RequestException:
            return None

        if not response.ok:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        if not isinstance(
            payload,
            dict,
        ):
            return None

        return payload

    @staticmethod
    def _extract_sample_answers(
        render_payload: dict[str, Any],
    ) -> dict[str, str]:
        question_inputs = (
            render_payload.get(
                "questioninputs",
                {},
            )
        )

        if not isinstance(
            question_inputs,
            dict,
        ):
            return {}

        answers: dict[str, str] = {}

        for (
            input_name,
            input_data,
        ) in question_inputs.items():
            if not isinstance(
                input_data,
                dict,
            ):
                continue

            sample_solution = (
                input_data.get(
                    "samplesolution"
                )
            )

            answer = (
                LiveTechnicalQuestionValidator
                ._extract_sample_value(
                    sample_solution
                )
            )

            if answer is not None:
                answers[
                    str(input_name)
                ] = answer

        return answers

    @staticmethod
    def _extract_sample_value(
        sample_solution: Any,
    ) -> str | None:
        if isinstance(
            sample_solution,
            str,
        ):
            value = sample_solution.strip()

            return value or None

        if isinstance(
            sample_solution,
            dict,
        ):
            for value in (
                sample_solution.values()
            ):
                if isinstance(
                    value,
                    str,
                ):
                    value = value.strip()

                    if value:
                        return value

        return None

    @staticmethod
    def _prt_executed(
        grade_payload: dict[str, Any],
    ) -> bool:
        prt_results = (
            grade_payload.get(
                "prtresults",
                {}
            )
        )

        if not isinstance(
            prt_results,
            dict,
        ):
            return False

        if not prt_results:
            return False

        for result in (
            prt_results.values()
        ):
            if not isinstance(
                result,
                dict,
            ):
                continue

            answer_notes = (
                result.get(
                    "answernotes",
                    []
                )
            )

            if answer_notes:
                return True

        return False
