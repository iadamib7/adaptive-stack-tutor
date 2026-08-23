from __future__ import annotations

from dataclasses import dataclass

from backend.app.integrations.stack_api.variant_deployer import (
    get_deployed_seeds,
)
from backend.app.learning.adaptive_tasks.extractor import (
    extract_adaptive_tasks,
)
from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.services.live_session_factory import (
    question_runtime_service,
)
from backend.app.services.session_service_factory import (
    MAPPING_PATH,
)


@dataclass
class QuestionResult:
    concept_id: str
    concept_name: str
    question_id: str
    question_name: str

    prepared: bool = False
    rendered: bool = False
    extracted: bool = False
    inputs_mapped: bool = False
    prts_mapped: bool = False

    variant_count: int = 0
    task_count: int = 0

    inputs: list[str] | None = None
    prts: list[str] | None = None

    failure_stage: str | None = None
    error: str | None = None

    @property
    def passed(self) -> bool:
        return all(
            [
                self.prepared,
                self.rendered,
                self.extracted,
                self.inputs_mapped,
                self.prts_mapped,
            ]
        )


def validate_question(
    *,
    concept_id: str,
    concept_name: str,
    question_id: str,
    question_name: str,
) -> QuestionResult:
    result = QuestionResult(
        concept_id=concept_id,
        concept_name=concept_name,
        question_id=question_id,
        question_name=question_name,
        inputs=[],
        prts=[],
    )

    # --------------------------------------------------
    # Stage 1: prepare / deploy
    # --------------------------------------------------

    try:
        question_xml, seed = (
            question_runtime_service.prepare_question(
                question_id
            )
        )

        seeds = get_deployed_seeds(
            question_xml
        )

        if not seeds:
            raise ValueError(
                "Prepared question has no deployed seeds."
            )

        result.prepared = True
        result.variant_count = len(
            seeds
        )

    except Exception as error:
        result.failure_stage = (
            "PREPARE / DEPLOY"
        )
        result.error = (
            f"{type(error).__name__}: {error}"
        )

        return result

    # --------------------------------------------------
    # Stage 2: render
    # --------------------------------------------------

    try:
        rendered = (
            question_runtime_service.render_question(
                question_id=question_id,
                seed=seed,
            )
        )

        html = rendered.get(
            "html",
            "",
        )

        if not isinstance(
            html,
            str,
        ):
            raise ValueError(
                "Rendered HTML is not a string."
            )

        if not html.strip():
            raise ValueError(
                "STACK returned empty rendered HTML."
            )

        result.rendered = True

    except Exception as error:
        result.failure_stage = "RENDER"
        result.error = (
            f"{type(error).__name__}: {error}"
        )

        return result

    # --------------------------------------------------
    # Stage 3: adaptive task extraction
    # --------------------------------------------------

    try:
        extracted = extract_adaptive_tasks(
            question_id=question_id,
            question_xml=question_xml,
        )

        if not extracted.tasks:
            raise ValueError(
                "No adaptive tasks were extracted."
            )

        result.extracted = True
        result.task_count = (
            extracted.task_count
        )

    except Exception as error:
        result.failure_stage = (
            "ADAPTIVE EXTRACTION"
        )
        result.error = (
            f"{type(error).__name__}: {error}"
        )

        return result

    # --------------------------------------------------
    # Stage 4: input mapping
    # --------------------------------------------------

    all_inputs: list[str] = []

    for task in extracted.tasks:
        if not task.input_names:
            result.failure_stage = (
                "INPUT MAPPING"
            )

            result.error = (
                f"Task {task.task_id} has "
                "no mapped inputs."
            )

            return result

        for input_name in (
            task.input_names
        ):
            if input_name not in all_inputs:
                all_inputs.append(
                    input_name
                )

    result.inputs = all_inputs
    result.inputs_mapped = True

    # --------------------------------------------------
    # Stage 5: PRT mapping
    # --------------------------------------------------

    all_prts: list[str] = []

    for task in extracted.tasks:
        if not task.prt_names:
            result.failure_stage = (
                "PRT MAPPING"
            )

            result.error = (
                f"Task {task.task_id} has "
                "no mapped PRTs."
            )

            return result

        for prt_name in (
            task.prt_names
        ):
            if prt_name not in all_prts:
                all_prts.append(
                    prt_name
                )

    result.prts = all_prts
    result.prts_mapped = True

    return result


def print_question_result(
    result: QuestionResult,
) -> None:
    status = (
        "PASS"
        if result.passed
        else "FAIL"
    )

    print(
        f"[{status}] "
        f"{result.question_id} - "
        f"{result.question_name}"
    )

    if result.passed:
        print(
            "       variants : "
            f"{result.variant_count}"
        )

        print(
            "       render   : OK"
        )

        print(
            "       tasks    : "
            f"{result.task_count}"
        )

        print(
            "       inputs   : "
            + ", ".join(
                result.inputs or []
            )
        )

        print(
            "       PRTs     : "
            + ", ".join(
                result.prts or []
            )
        )

    else:
        print(
            "       stage    : "
            f"{result.failure_stage}"
        )

        print(
            "       error    : "
            f"{result.error}"
        )

    print()


def main() -> None:
    curriculum = (
        load_curriculum_question_map(
            MAPPING_PATH
        )
    )

    print()
    print(
        "=" * 72
    )
    print(
        "ADAPTIVE STACK CURRICULUM "
        "COMPATIBILITY SWEEP"
    )
    print(
        "=" * 72
    )
    print()

    results: list[
        QuestionResult
    ] = []

    for mapping in curriculum.mappings:
        print(
            "-" * 72
        )

        print(
            f"CONCEPT: "
            f"{mapping.concept_name} "
            f"({mapping.concept_id})"
        )

        print(
            "-" * 72
        )
        print()

        ordered_questions = sorted(
            mapping.questions,
            key=lambda question: (
                question.sequence_order,
                question.question_id,
            ),
        )

        for question in (
            ordered_questions
        ):
            result = validate_question(
                concept_id=(
                    mapping.concept_id
                ),
                concept_name=(
                    mapping.concept_name
                ),
                question_id=(
                    question.question_id
                ),
                question_name=(
                    question.question_name
                ),
            )

            results.append(
                result
            )

            print_question_result(
                result
            )

    passed = sum(
        result.passed
        for result in results
    )

    failed = (
        len(results)
        - passed
    )

    print(
        "=" * 72
    )
    print(
        "FINAL COMPATIBILITY SUMMARY"
    )
    print(
        "=" * 72
    )

    print(
        f"TOTAL QUESTIONS : "
        f"{len(results)}"
    )

    print(
        f"PASS            : "
        f"{passed}"
    )

    print(
        f"FAIL            : "
        f"{failed}"
    )

    if failed:
        print()
        print(
            "FAILED QUESTIONS"
        )
        print(
            "-" * 72
        )

        for result in results:
            if result.passed:
                continue

            print(
                f"{result.question_id} | "
                f"{result.concept_name} | "
                f"{result.failure_stage}"
            )

            print(
                f"    {result.error}"
            )

    print(
        "=" * 72
    )

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
