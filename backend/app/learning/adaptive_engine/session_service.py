from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from xml.etree import ElementTree

from backend.app.integrations.stack_api.client import (
    StackEvaluationClient,
)

from backend.app.integrations.stack_api.models import (
    StackEvaluationRequest,
)

from backend.app.learning.adaptive_engine.engine import (
    CurriculumIndependentAdaptiveEngine,
)

from backend.app.learning.adaptive_engine.adaptive_graph_builder import (
    StackAdaptiveGraphBuilder,
)

from backend.app.learning.adaptive_engine.bank_profile import (
    StackBankProfiler,
)

from backend.app.learning.adaptive_engine.metadata import (
    AdaptiveMetadataLoader,
)

from backend.app.learning.adaptive_engine.models import (
    AdaptiveDecision,
)

from backend.app.learning.adaptive_engine.question_bank import (
    AdaptiveQuestionBank,
    StackXmlQuestionBankImporter,
)

from backend.app.learning.adaptive_engine.stack_evidence import (
    StackEvidenceAdapter,
)

from backend.app.learning.adaptive_engine.stack_runtime import (
    AdaptiveStackRenderer,
    RenderedAdaptiveQuestion,
)


@dataclass(frozen=True)
class AdaptiveSessionView:
    learner_id: int

    question_id: str
    title: str

    seed: int

    html: str
    inputs: dict[str, object]

    ability: float

    decision_reason: str

    decision_type: str = "advance"

    return_target_question_id: (
        str | None
    ) = None

    previous_score: float | None = None

    previous_outcome: str | None = None


class GenericAdaptiveSessionService:
    """
    One curriculum-independent adaptive workflow.

    Instructor content enters as STACK/Moodle XML.

    STACK owns grading, PRT execution, and feedback.

    This service owns learner state and
    cross-question adaptation.
    """

    def __init__(
        self,
        *,
        question_bank: AdaptiveQuestionBank,
        evaluation_client:
            StackEvaluationClient,
        renderer: AdaptiveStackRenderer,
        outcome_aliases: (
            dict[
                str,
                dict[str, str],
            ]
            | None
        ) = None,
    ) -> None:
        self.question_bank = (
            question_bank
        )

        self.engine = (
            CurriculumIndependentAdaptiveEngine(
                question_bank
                .adaptive_questions()
            )
        )

        self.evaluation_client = (
            evaluation_client
        )

        self.renderer = renderer

        self.evidence_adapter = (
            StackEvidenceAdapter()
        )

        self.outcome_aliases = (
            outcome_aliases or {}
        )

        self._current_question: dict[
            int,
            str,
        ] = {}

        self._current_seed: dict[
            int,
            int,
        ] = {}

    @classmethod
    def from_xml(
        cls,
        *,
        xml_text: str,
        evaluation_client:
            StackEvaluationClient,
        renderer: AdaptiveStackRenderer,
        metadata_json:
            str | None = None,
        outcome_aliases: (
            dict[
                str,
                dict[str, str],
            ]
            | None
        ) = None,
    ) -> (
        GenericAdaptiveSessionService
    ):
        importer = (
            StackXmlQuestionBankImporter()
        )

        bank = importer.import_text(
            xml_text
        )

        # Build conservative bank-local adaptive
        # structure automatically from trustworthy
        # STACK profile evidence.
        #
        # XML storage order never defines the
        # learning sequence.
        profile = (
            StackBankProfiler()
            .profile_text(
                xml_text
            )
        )

        graph_result = (
            StackAdaptiveGraphBuilder()
            .build(
                bank=bank,
                profile=profile,
            )
        )

        bank = graph_result.bank

        manifest_aliases: dict[
            str,
            dict[str, str],
        ] = {}

        if (
            metadata_json is not None
            and metadata_json.strip()
        ):
            metadata_loader = (
                AdaptiveMetadataLoader()
            )

            manifest = (
                metadata_loader.load_text(
                    metadata_json
                )
            )

            bank = metadata_loader.apply(
                bank=bank,
                manifest=manifest,
            )

            manifest_aliases = (
                manifest.outcome_aliases()
            )

        combined_aliases: dict[
            str,
            dict[str, str],
        ] = {
            question_id: dict(
                aliases
            )
            for (
                question_id,
                aliases,
            ) in (
                graph_result
                .outcome_aliases
                .items()
            )
        }

        for (
            question_id,
            aliases,
        ) in manifest_aliases.items():
            combined_aliases.setdefault(
                question_id,
                {},
            ).update(
                aliases
            )

        if outcome_aliases:
            for (
                question_id,
                aliases,
            ) in outcome_aliases.items():
                combined_aliases.setdefault(
                    question_id,
                    {},
                ).update(
                    aliases
                )

        return cls(
            question_bank=bank,
            evaluation_client=(
                evaluation_client
            ),
            renderer=renderer,
            outcome_aliases=(
                combined_aliases
            ),
        )

    def start(
        self,
        *,
        learner_id: int,
    ) -> AdaptiveSessionView:
        decision = self.engine.start(
            learner_id
        )

        if decision is None:
            raise RuntimeError(
                "No adaptive question "
                "is available."
            )

        return self._render_decision(
            learner_id=learner_id,
            decision=decision,
        )

    def submit_answer(
        self,
        *,
        learner_id: int,
        student_answers:
            dict[str, str],
    ) -> AdaptiveSessionView:
        question_id = (
            self._current_question.get(
                learner_id
            )
        )

        seed = (
            self._current_seed.get(
                learner_id
            )
        )

        if (
            question_id is None
            or seed is None
        ):
            raise ValueError(
                "Learner does not have "
                "an active adaptive question."
            )

        imported = (
            self.question_bank.require(
                question_id
            )
        )

        result = (
            self.evaluation_client.evaluate(
                StackEvaluationRequest(
                    question_id=(
                        question_id
                    ),
                    question_xml=(
                        imported.stack_xml
                    ),
                    student_answers=(
                        student_answers
                    ),
                    seed=seed,
                )
            )
        )

        if not result.valid:
            raise ValueError(
                "STACK could not grade "
                "the learner response: "
                + "; ".join(
                    result.errors
                )
            )

        evidence = (
            self.evidence_adapter
            .from_normalized_result(
                result=result,
                outcome_aliases=(
                    self.outcome_aliases
                    .get(
                        question_id
                    )
                ),
            )
        )

        decision = self.engine.submit(
            learner_id=learner_id,
            evidence=evidence,
        )

        if decision is None:
            raise RuntimeError(
                "Adaptive session has "
                "no next question."
            )

        return self._render_decision(
            learner_id=learner_id,
            decision=decision,
            previous_score=(
                evidence.score
            ),
            previous_outcome=(
                evidence.prt_outcome
            ),
        )

    def _render_decision(
        self,
        *,
        learner_id: int,
        decision: AdaptiveDecision,
        previous_score:
            float | None = None,
        previous_outcome:
            str | None = None,
    ) -> AdaptiveSessionView:
        question_id = (
            decision.question.question_id
        )

        imported = (
            self.question_bank.require(
                question_id
            )
        )

        seed = self._seed_for_question(
            learner_id=learner_id,
            question_id=question_id,
            question_xml=(
                imported.stack_xml
            ),
        )

        rendered = self.renderer.render(
            question_id=question_id,
            question_xml=(
                imported.stack_xml
            ),
            seed=seed,
        )

        self._current_question[
            learner_id
        ] = question_id

        self._current_seed[
            learner_id
        ] = seed

        learner = (
            self.engine
            .get_or_create_learner(
                learner_id
            )
        )

        return AdaptiveSessionView(
            learner_id=learner_id,
            question_id=question_id,
            title=(
                decision.question.title
            ),
            seed=rendered.seed,
            html=rendered.html,
            inputs=rendered.inputs,
            ability=learner.ability,
            decision_reason=(
                decision.reason
            ),
            decision_type=(
                decision.decision_type
            ),
            return_target_question_id=(
                decision
                .return_target_question_id
            ),
            previous_score=(
                previous_score
            ),
            previous_outcome=(
                previous_outcome
            ),
        )

    @classmethod
    def _seed_for_question(
        cls,
        *,
        learner_id: int,
        question_id: str,
        question_xml: str,
    ) -> int:
        """
        Select a valid deterministic seed.

        Native STACK questions may contain one or
        more <deployedseed> values. When they do,
        STACK requires rendering/grading to use
        one of those deployed variants.

        Questions without deployed variants keep
        using the generic deterministic seed.
        """

        stable_seed = cls._stable_seed(
            learner_id=learner_id,
            question_id=question_id,
        )

        try:
            root = ElementTree.fromstring(
                question_xml
            )
        except ElementTree.ParseError:
            return stable_seed

        deployed_seeds: list[int] = []

        for element in root.findall(
            ".//deployedseed"
        ):
            raw_value = (
                element.text or ""
            ).strip()

            if not raw_value:
                continue

            try:
                value = int(
                    raw_value
                )
            except ValueError:
                continue

            if value > 0:
                deployed_seeds.append(
                    value
                )

        if not deployed_seeds:
            return stable_seed

        # Deterministically distribute learners
        # across the question's real deployed
        # variants.
        index = (
            stable_seed
            % len(
                deployed_seeds
            )
        )

        return deployed_seeds[
            index
        ]

    @staticmethod
    def _stable_seed(
        *,
        learner_id: int,
        question_id: str,
    ) -> int:
        value = (
            f"{learner_id}:"
            f"{question_id}"
        )

        digest = sha256(
            value.encode("utf-8")
        ).hexdigest()

        return (
            int(
                digest[:8],
                16,
            )
            % 2_000_000_000
        ) + 1
