from __future__ import annotations

from collections import defaultdict
import csv
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from backend.app.learning.session.models import (
    ScoredStackOutcome,
)
from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.services.session_service_factory import (
    build_mock_stack_session_service,
)


GHANA_MAPPING_PATH = Path(
    "examples/curriculum_mapping/"
    "ghana_basic9_linear_readiness.json"
)

RESEARCH_OUTPUT_DIR = Path(
    "resources/generated/research"
)

MAX_STEPS = 100
MAX_SAME_QUESTION_REPEATS = 6


@dataclass(frozen=True)
class TraceStep:
    step: int
    concept_id: str
    question_id: str
    score: float
    action: str
    next_concept_id: str | None
    mastered: bool
    evidence_score: float


@dataclass
class SimulationResult:
    profile: str
    trace: list[TraceStep]
    completed: bool
    stalled: bool
    reason: str


def build_question_metadata():
    curriculum = load_curriculum_question_map(
        GHANA_MAPPING_PATH
    )

    mastery_questions: set[str] = set()

    concept_names: dict[str, str] = {}

    question_names: dict[str, str] = {}

    for mapping in curriculum.mappings:
        concept_names[
            mapping.concept_id
        ] = mapping.concept_name

        for question in mapping.questions:
            question_names[
                question.question_id
            ] = question.question_name

            if question.required_for_mastery:
                mastery_questions.add(
                    question.question_id
                )

    return (
        curriculum,
        mastery_questions,
        concept_names,
        question_names,
    )


def score_for_profile(
    *,
    profile: str,
    question_id: str,
    mastery_questions: set[str],
    question_attempts: dict[str, int],
) -> float:
    attempts = question_attempts[
        question_id
    ]

    if profile == "STRONG":
        return 1.0

    if profile == "MIXED":
        if question_id in mastery_questions:
            return 1.0

        if attempts == 1:
            return 0.5

        return 1.0

    if profile == "STRUGGLING":
        return 0.0

    raise ValueError(
        f"Unknown profile: {profile}"
    )


def simulate(
    profile: str,
) -> SimulationResult:
    (
        curriculum,
        mastery_questions,
        _,
        _,
    ) = build_question_metadata()

    service, _ = (
        build_mock_stack_session_service(
            mapping_path=GHANA_MAPPING_PATH,
        )
    )

    engine = service.session_engine

    student_id = 1

    starting_concept = (
        curriculum.mappings[0].concept_id
    )

    state = engine.start_session(
        student_id=student_id,
        concept_id=starting_concept,
    )

    trace: list[TraceStep] = []

    question_attempts: dict[
        str,
        int,
    ] = defaultdict(int)

    same_question_repeats = 0
    previous_question_id = None

    for step in range(
        1,
        MAX_STEPS + 1,
    ):
        # ----------------------------------------------
        # Handle concept transition.
        # ----------------------------------------------

        if state.session_complete:
            if state.next_concept_id is None:
                return SimulationResult(
                    profile=profile,
                    trace=trace,
                    completed=True,
                    stalled=False,
                    reason=(
                        "No further concept remains."
                    ),
                )

            state = engine.start_session(
                student_id=student_id,
                concept_id=(
                    state.next_concept_id
                ),
            )

        if state.question is None:
            return SimulationResult(
                profile=profile,
                trace=trace,
                completed=False,
                stalled=True,
                reason=(
                    "The session produced no next "
                    "question."
                ),
            )

        question_id = state.question.id

        # ----------------------------------------------
        # Detect deterministic dead loops.
        # ----------------------------------------------

        if question_id == previous_question_id:
            same_question_repeats += 1
        else:
            same_question_repeats = 1

        previous_question_id = question_id

        if (
            same_question_repeats
            > MAX_SAME_QUESTION_REPEATS
        ):
            return SimulationResult(
                profile=profile,
                trace=trace,
                completed=False,
                stalled=True,
                reason=(
                    "The same question was selected "
                    "too many times consecutively: "
                    f"{question_id}."
                ),
            )

        question_attempts[
            question_id
        ] += 1

        score = score_for_profile(
            profile=profile,
            question_id=question_id,
            mastery_questions=(
                mastery_questions
            ),
            question_attempts=(
                question_attempts
            ),
        )

        outcome_code = (
            "correct"
            if score >= 1.0
            else (
                "partial"
                if score > 0.0
                else "incorrect"
            )
        )

        concept_before = (
            state.current_concept_id
        )

        state = engine.submit_outcome(
            ScoredStackOutcome(
                student_id=student_id,
                concept_id=concept_before,
                question_id=question_id,
                outcome_code=outcome_code,
                score=score,
                stack_feedback=None,
            )
        )

        trace.append(
            TraceStep(
                step=step,
                concept_id=concept_before,
                question_id=question_id,
                score=score,
                action=state.action.value,
                next_concept_id=(
                    state.next_concept_id
                ),
                mastered=(
                    state.progress
                    .concept_mastered
                ),
                evidence_score=(
                    state.progress
                    .evidence_score
                ),
            )
        )

    return SimulationResult(
        profile=profile,
        trace=trace,
        completed=False,
        stalled=True,
        reason=(
            f"Maximum step count "
            f"({MAX_STEPS}) reached."
        ),
    )


def normalized_trace(
    result: SimulationResult,
) -> list[tuple]:
    return [
        (
            step.concept_id,
            step.question_id,
            step.score,
            step.action,
            step.next_concept_id,
            step.mastered,
            round(
                step.evidence_score,
                6,
            ),
        )
        for step in result.trace
    ]


def trace_fingerprint(
    result: SimulationResult,
) -> str:
    payload = json.dumps(
        normalized_trace(result),
        separators=(",", ":"),
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def build_summary_row(
    *,
    result: SimulationResult,
    mastery_questions: set[str],
) -> dict[str, object]:
    total_steps = len(
        result.trace
    )

    attempted_question_ids = [
        step.question_id
        for step in result.trace
    ]

    unique_questions = set(
        attempted_question_ids
    )

    mastery_attempts = sum(
        1
        for question_id
        in attempted_question_ids
        if question_id
        in mastery_questions
    )

    repeated_attempts = (
        total_steps
        - len(unique_questions)
    )

    final_evidence_score = (
        result.trace[-1].evidence_score
        if result.trace
        else 0.0
    )

    mastered_steps = sum(
        1
        for step in result.trace
        if step.mastered
    )

    return {
        "profile": result.profile,
        "total_steps": total_steps,
        "unique_questions_attempted": (
            len(unique_questions)
        ),
        "repeated_attempts": (
            repeated_attempts
        ),
        "mastery_question_attempts": (
            mastery_attempts
        ),
        "mastered_steps": mastered_steps,
        "final_evidence_score": round(
            final_evidence_score,
            6,
        ),
        "completed": result.completed,
        "stalled": result.stalled,
        "reason": result.reason,
        "trace_sha256": (
            trace_fingerprint(result)
        ),
    }


def export_research_results(
    *,
    results: dict[
        str,
        SimulationResult,
    ],
    mastery_questions: set[str],
) -> tuple[Path, Path]:
    RESEARCH_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        RESEARCH_OUTPUT_DIR
        / (
            "adaptive_pathway_"
            "simulation_summary.csv"
        )
    )

    traces_path = (
        RESEARCH_OUTPUT_DIR
        / (
            "adaptive_pathway_"
            "simulation_traces.json"
        )
    )

    rows = [
        build_summary_row(
            result=results[profile],
            mastery_questions=(
                mastery_questions
            ),
        )
        for profile in results
    ]

    fieldnames = [
        "profile",
        "total_steps",
        "unique_questions_attempted",
        "repeated_attempts",
        "mastery_question_attempts",
        "mastered_steps",
        "final_evidence_score",
        "completed",
        "stalled",
        "reason",
        "trace_sha256",
    ]

    with summary_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(
            rows
        )

    traces_payload = {
        "simulation_type": (
            "deterministic_mock_learner"
        ),
        "curriculum_mapping": str(
            GHANA_MAPPING_PATH
        ),
        "profiles": {},
    }

    for profile, result in (
        results.items()
    ):
        traces_payload[
            "profiles"
        ][profile] = {
            "summary": build_summary_row(
                result=result,
                mastery_questions=(
                    mastery_questions
                ),
            ),
            "trace": [
                {
                    "step": step.step,
                    "concept_id": (
                        step.concept_id
                    ),
                    "question_id": (
                        step.question_id
                    ),
                    "score": step.score,
                    "action": step.action,
                    "next_concept_id": (
                        step.next_concept_id
                    ),
                    "mastered": (
                        step.mastered
                    ),
                    "evidence_score": round(
                        step.evidence_score,
                        6,
                    ),
                }
                for step in result.trace
            ],
        }

    traces_path.write_text(
        json.dumps(
            traces_payload,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return (
        summary_path,
        traces_path,
    )


def print_result(
    result: SimulationResult,
    concept_names: dict[str, str],
    question_names: dict[str, str],
) -> None:
    print()
    print("=" * 78)
    print(
        f"{result.profile} LEARNER"
    )
    print("=" * 78)

    last_concept = None

    for step in result.trace:
        if step.concept_id != last_concept:
            print()
            print(
                "CONCEPT: "
                + concept_names.get(
                    step.concept_id,
                    step.concept_id,
                )
            )

            last_concept = (
                step.concept_id
            )

        question_name = (
            question_names.get(
                step.question_id,
                step.question_id,
            )
        )

        print(
            f"{step.step:02d}. "
            f"{step.question_id} "
            f"| score={step.score:.2f} "
            f"| evidence="
            f"{step.evidence_score:.2f} "
            f"| {step.action}"
        )

        print(
            f"    {question_name}"
        )

        if step.next_concept_id:
            print(
                "    next concept -> "
                + concept_names.get(
                    step.next_concept_id,
                    step.next_concept_id,
                )
            )

    print()
    print(
        "STATUS: "
        + (
            "COMPLETED"
            if result.completed
            else "STALLED"
        )
    )

    print(
        "STEPS: "
        f"{len(result.trace)}"
    )

    print(
        "REASON: "
        f"{result.reason}"
    )


def main() -> None:
    (
        _,
        mastery_questions,
        concept_names,
        question_names,
    ) = build_question_metadata()

    profiles = [
        "STRONG",
        "MIXED",
        "STRUGGLING",
    ]

    first_runs: dict[
        str,
        SimulationResult,
    ] = {}

    print()
    print("=" * 78)
    print(
        "DETERMINISTIC ADAPTIVE "
        "PATHWAY SIMULATION"
    )
    print("=" * 78)

    for profile in profiles:
        first = simulate(
            profile
        )

        second = simulate(
            profile
        )

        first_runs[
            profile
        ] = first

        deterministic = (
            normalized_trace(first)
            == normalized_trace(second)
            and first.completed
            == second.completed
            and first.stalled
            == second.stalled
        )

        if not deterministic:
            raise AssertionError(
                f"{profile} pathway was "
                "not deterministic."
            )

        print_result(
            result=first,
            concept_names=concept_names,
            question_names=question_names,
        )

        print(
            "DETERMINISTIC REPEAT: PASS"
        )

    strong_trace = normalized_trace(
        first_runs["STRONG"]
    )

    mixed_trace = normalized_trace(
        first_runs["MIXED"]
    )

    struggling_trace = normalized_trace(
        first_runs["STRUGGLING"]
    )

    print()
    print("=" * 78)
    print(
        "FINAL ADAPTIVITY SUMMARY"
    )
    print("=" * 78)

    print(
        "Strong deterministic     : PASS"
    )

    print(
        "Mixed deterministic      : PASS"
    )

    print(
        "Struggling deterministic : PASS"
    )

    print(
        "Strong != Mixed          : "
        + (
            "PASS"
            if strong_trace != mixed_trace
            else "FAIL"
        )
    )

    print(
        "Strong != Struggling     : "
        + (
            "PASS"
            if strong_trace
            != struggling_trace
            else "FAIL"
        )
    )

    print(
        "Mixed != Struggling      : "
        + (
            "PASS"
            if mixed_trace
            != struggling_trace
            else "FAIL"
        )
    )

    print()
    print(
        "Strong completed         : "
        f"{first_runs['STRONG'].completed}"
    )

    print(
        "Mixed completed          : "
        f"{first_runs['MIXED'].completed}"
    )

    print(
        "Struggling completed     : "
        f"{first_runs['STRUGGLING'].completed}"
    )

    summary_path, traces_path = (
        export_research_results(
            results=first_runs,
            mastery_questions=(
                mastery_questions
            ),
        )
    )

    print()
    print(
        "Research summary CSV     : "
        f"{summary_path}"
    )

    print(
        "Research traces JSON     : "
        f"{traces_path}"
    )

    print("=" * 78)


if __name__ == "__main__":
    main()
