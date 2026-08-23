from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import requests

from backend.app.integrations.stack_api.variant_deployer import (
    StackVariantDeployer,
    add_deployed_seeds,
    get_deployed_seeds,
)
from backend.app.integrations.stack_xml.question_extractor import (
    extract_stack_question,
)


class StackQuestionRuntimeError(RuntimeError):
    pass


class StackQuestionRuntimeService:
    """
    Prepare and render real STACK questions for learners.

    Original third-party XML is never changed. Extracted and
    deployed copies are written only under resources/generated.
    """

    def __init__(
        self,
        export_path: Path,
        generated_directory: Path,
        base_url: str = "http://localhost:3080",
        deployed_variant_count: int = 5,
        timeout_seconds: int = 120,
        additional_generated_directories: (
            tuple[Path, ...]
        ) = (),
    ) -> None:
        self.export_path = export_path

        # Primary directory remains the write location
        # for questions extracted from the curriculum's
        # legacy STACK export.
        self.generated_directory = generated_directory

        # Additional directories are read-only lookup
        # locations for shared, curriculum-independent
        # deployed questions.
        self.additional_generated_directories = (
            additional_generated_directories
        )

        self.base_url = base_url.rstrip("/")
        self.deployed_variant_count = (
            deployed_variant_count
        )
        self.timeout_seconds = timeout_seconds

        self.session = requests.Session()

    def prepare_question(
        self,
        question_id: str,
    ) -> tuple[str, int]:
        deployed_path = (
            self._find_existing_deployed_path(
                question_id
            )
        )

        if deployed_path is not None:
            question_xml = deployed_path.read_text(
                encoding="utf-8"
            )

            seeds = get_deployed_seeds(
                question_xml
            )

            if seeds:
                return question_xml, seeds[0]

        # Nothing deployable was found in either the
        # curriculum-specific directory or any shared
        # question directory. Fall back to extracting
        # the question from the curriculum export.
        deployed_path = self._deployed_path(
            question_id
        )

        print(

            "\n===== PREPARING STACK QUESTION ====="

        )

        print(

            f"question_id = {question_id}"

        )

        print(

            "====================================\n"

        )


        authored_xml = extract_stack_question(
            export_path=self.export_path,
            question_id=question_id,
        )

        existing_seeds = get_deployed_seeds(
            authored_xml
        )

        if existing_seeds:
            deployed_xml = authored_xml
            seeds = existing_seeds
        else:
            deployer = StackVariantDeployer(
                base_url=self.base_url,
                timeout_seconds=self.timeout_seconds,
            )

            deployment = deployer.deploy(
                question_xml=authored_xml,
                variant_count=(
                    self.deployed_variant_count
                ),
                max_attempts=150,
            )

            deployed_xml = deployment.question_xml
            seeds = deployment.seeds

        deployed_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        deployed_path.write_text(
            deployed_xml,
            encoding="utf-8",
        )

        return deployed_xml, seeds[0]

    def render_question(
        self,
        question_id: str,
        seed: int | None = None,
    ) -> dict[str, Any]:
        question_xml, default_seed = (
            self.prepare_question(question_id)
        )

        selected_seed = (
            seed
            if seed is not None
            else default_seed
        )

        response = self.session.post(
            f"{self.base_url}/render",
            json={
                "questionDefinition": question_xml,
                "seed": selected_seed,
                "renderInputs": "student-",
                "fullRender": [
                    "validation-",
                    "feedback-",
                ],
                "readOnly": False,
            },
            timeout=self.timeout_seconds,
        )

        payload = self._read_response(
            response=response,
            operation="render",
        )

        question_html = payload.get(
            "questionrender",
            "",
        )

        question_inputs = payload.get(
            "questioninputs",
            {},
        )

        if not isinstance(
            question_inputs,
            dict,
        ):
            raise StackQuestionRuntimeError(
                "STACK returned invalid question inputs."
            )

        return {
            "question_id": question_id,
            "seed": selected_seed,
            "question_xml": question_xml,
            "html": question_html,
            "inputs": question_inputs,
            "worked_solution": payload.get(
                "questionsamplesolutiontext",
                "",
            ),
            "question_note": payload.get(
                "questionnote",
                "",
            ),
            "available_variants": payload.get(
                "questionvariants",
                [],
            ),
        }

    @staticmethod
    def _read_response(
        response: requests.Response,
        operation: str,
    ) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as error:
            raise StackQuestionRuntimeError(
                f"STACK returned a non-JSON "
                f"{operation} response."
            ) from error

        if not response.ok:
            message = payload.get(
                "message",
                f"STACK {operation} failed.",
            )

            raise StackQuestionRuntimeError(
                str(message)
            )

        if not isinstance(payload, dict):
            raise StackQuestionRuntimeError(
                f"STACK returned an unexpected "
                f"{operation} response."
            )

        return payload

    def _find_existing_deployed_path(
        self,
        question_id: str,
    ) -> Path | None:
        filename = (
            f"{question_id}_deployed.xml"
        )

        search_directories = (
            self.generated_directory,
            *self.additional_generated_directories,
        )

        for directory in search_directories:
            candidate = (
                directory
                / filename
            )

            if candidate.is_file():
                return candidate

        return None

    def _deployed_path(
        self,
        question_id: str,
    ) -> Path:
        """
        Return the primary write path.

        Shared directories are lookup-only. Questions
        extracted from a curriculum export continue to
        be deployed into that curriculum's own generated
        directory.
        """

        return (
            self.generated_directory
            / f"{question_id}_deployed.xml"
        )
