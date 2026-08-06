from __future__ import annotations

from dataclasses import dataclass
import random
from xml.etree import ElementTree as ET

import requests


MAX_STACK_SEED = 2_147_483_647


class StackVariantDeploymentError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeployedVariant:
    seed: int
    question_note: str


@dataclass(frozen=True)
class VariantDeploymentResult:
    question_xml: str
    variants: list[DeployedVariant]

    @property
    def seeds(self) -> list[int]:
        return [
            variant.seed
            for variant in self.variants
        ]


def get_deployed_seeds(
    question_xml: str,
) -> list[int]:
    root = ET.fromstring(question_xml)
    question = _get_stack_question(root)

    return [
        int(element.text)
        for element in question.findall(
            "deployedseed"
        )
        if element.text
        and element.text.strip()
    ]


def add_deployed_seeds(
    question_xml: str,
    seeds: list[int],
) -> str:
    root = ET.fromstring(question_xml)
    question = _get_stack_question(root)

    for element in question.findall(
        "deployedseed"
    ):
        question.remove(element)

    for seed in seeds:
        if seed <= 0:
            raise ValueError(
                "STACK seeds must be positive integers."
            )

        deployed_seed = ET.Element(
            "deployedseed"
        )
        deployed_seed.text = str(seed)

        question.append(deployed_seed)

    return ET.tostring(
        root,
        encoding="unicode",
    )


class StackVariantDeployer:
    """
    Prepare authored randomized STACK questions for the
    standalone API by selecting tested, distinct variants.

    The original source XML is never modified. The caller
    chooses where to save the generated deployed copy.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3080",
        timeout_seconds: int = 120,
        session: requests.Session | None = None,
        random_generator: random.Random | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

        self.session = (
            session
            if session is not None
            else requests.Session()
        )

        self.random_generator = (
            random_generator
            if random_generator is not None
            else random.SystemRandom()
        )

    def deploy(
        self,
        question_xml: str,
        variant_count: int = 5,
        max_attempts: int = 100,
    ) -> VariantDeploymentResult:
        if variant_count < 1:
            raise ValueError(
                "variant_count must be at least 1."
            )

        if variant_count > 100:
            raise ValueError(
                "No more than 100 variants may be "
                "deployed in one operation."
            )

        if max_attempts < variant_count:
            raise ValueError(
                "max_attempts cannot be smaller than "
                "variant_count."
            )

        accepted: list[DeployedVariant] = []
        accepted_seeds: set[int] = set()
        accepted_signatures: set[str] = set()

        attempts = 0

        while (
            len(accepted) < variant_count
            and attempts < max_attempts
        ):
            attempts += 1

            seed = self.random_generator.randint(
                1,
                MAX_STACK_SEED,
            )

            if seed in accepted_seeds:
                continue

            candidate_xml = add_deployed_seeds(
                question_xml=question_xml,
                seeds=[seed],
            )

            if not self._candidate_passes_tests(
                question_xml=candidate_xml,
                seed=seed,
            ):
                continue

            render_data = self._render_variant(
                question_xml=candidate_xml,
                seed=seed,
            )

            if render_data is None:
                continue

            question_note = render_data[
                "question_note"
            ]

            signature = render_data[
                "signature"
            ]

            if signature in accepted_signatures:
                continue

            accepted.append(
                DeployedVariant(
                    seed=seed,
                    question_note=question_note,
                )
            )

            accepted_seeds.add(seed)
            accepted_signatures.add(signature)

        if len(accepted) < variant_count:
            raise StackVariantDeploymentError(
                "Could not deploy the requested number "
                f"of distinct variants. Requested "
                f"{variant_count}, accepted "
                f"{len(accepted)}, attempted {attempts}."
            )

        deployed_xml = add_deployed_seeds(
            question_xml=question_xml,
            seeds=[
                variant.seed
                for variant in accepted
            ],
        )

        return VariantDeploymentResult(
            question_xml=deployed_xml,
            variants=accepted,
        )

    def _candidate_passes_tests(
        self,
        question_xml: str,
        seed: int,
    ) -> bool:
        response = self.session.post(
            f"{self.base_url}/test",
            json={
                "questionDefinition": question_xml,
            },
            timeout=self.timeout_seconds,
        )

        if not response.ok:
            return False

        payload = response.json()

        if payload.get("messages"):
            return False

        if payload.get("isupgradeerror"):
            return False

        results = payload.get("results", {})

        seed_result = results.get(str(seed))

        if seed_result is None:
            return False

        if seed_result.get("messages"):
            return False

        fails = seed_result.get("fails")

        if fails not in (0, None):
            return False

        return True

    def _render_variant(
        self,
        question_xml: str,
        seed: int,
    ) -> dict[str, str] | None:
        response = self.session.post(
            f"{self.base_url}/render",
            json={
                "questionDefinition": question_xml,
                "seed": seed,
            },
            timeout=self.timeout_seconds,
        )

        if not response.ok:
            return None

        payload = response.json()

        question_note = payload.get(
            "questionnote",
            "",
        )

        question_render = payload.get(
            "questionrender",
            "",
        )

        if not isinstance(question_note, str):
            question_note = ""

        if not isinstance(question_render, str):
            question_render = ""

        normalized_render = " ".join(
            question_render.split()
        )

        normalized_note = " ".join(
            question_note.split()
        )

        # The rendered question is the preferred signature
        # because some authored questions contain a constant
        # or incorrectly configured question note.
        signature = (
            normalized_render
            if normalized_render
            else normalized_note
        )

        if not signature:
            return None

        return {
            "question_note": question_note,
            "signature": signature,
        }


def _get_stack_question(
    root: ET.Element,
) -> ET.Element:
    if (
        root.tag == "question"
        and root.get("type") == "stack"
    ):
        return root

    for question in root.findall("question"):
        if question.get("type") == "stack":
            return question

    raise ValueError(
        "The XML does not contain a STACK question."
    )
