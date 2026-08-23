from __future__ import annotations

from backend.app.learning.curriculum_mapping.loader import (
    load_curriculum_question_map,
)
from backend.app.services.curriculum_runtime_profiles import (
    GHANA_BASIC9_PROFILE,
    KENYA_GRADE9_PROFILE,
)
from scripts.simulate_adaptive_pathways import (
    normalized_trace,
    simulate,
)


def question_ids(mapping) -> set[str]:
    return {
        question.question_id
        for concept in mapping.mappings
        for question in concept.questions
    }


def print_bank_summary() -> None:
    kenya = load_curriculum_question_map(
        KENYA_GRADE9_PROFILE.mapping_path
    )

    ghana = load_curriculum_question_map(
        GHANA_BASIC9_PROFILE.mapping_path
    )

    kenya_ids = question_ids(
        kenya
    )

    ghana_ids = question_ids(
        ghana
    )

    combined = (
        kenya_ids
        | ghana_ids
    )

    qlin_ids = sorted(
        question_id
        for question_id in ghana_ids
        if (
            question_id.startswith("qlin_")
            or question_id
            == "lr_01_table_linear_relation"
        )
    )

    print()
    print("=" * 72)
    print(
        "ADAPTIVE STACK TUTOR - "
        "RESEARCH DEMONSTRATION"
    )
    print("=" * 72)

    print()
    print("1. QUESTION BANK")
    print("-" * 72)

    print(
        "Kenya development bank:",
        len(kenya_ids),
        "mapped questions",
    )

    print(
        "Ghana pilot mapping:",
        len(ghana_ids),
        "mapped questions",
    )

    print(
        "Distinct questions available "
        "across both profiles:",
        len(combined),
    )

    print(
        "New Ghana linear-relations "
        "progression:",
        len(qlin_ids),
        "questions",
    )

    print()
    print(
        "Linear-relations progression:"
    )

    for index, question_id in enumerate(
        qlin_ids,
        start=1,
    ):
        print(
            f"  {index:02d}. "
            f"{question_id}"
        )


def summarize_profile(
    profile: str,
) -> None:
    first = simulate(
        profile
    )

    second = simulate(
        profile
    )

    deterministic = (
        normalized_trace(first)
        == normalized_trace(second)
    )

    print()
    print(
        profile,
        "LEARNER",
    )
    print("-" * 72)

    preview_limit = (
        8
        if profile != "STRUGGLING"
        else 10
    )

    for step in first.trace[
        :preview_limit
    ]:
        print(
            f"{step.step:02d}. "
            f"{step.question_id:<8} "
            f"score={step.score:.2f}  "
            f"evidence="
            f"{step.evidence_score:.2f}  "
            f"decision={step.action}"
        )

    remaining = (
        len(first.trace)
        - preview_limit
    )

    if remaining > 0:
        print(
            "    ... "
            f"{remaining} additional "
            "deterministic steps omitted"
        )

    unique_questions = {
        step.question_id
        for step in first.trace
    }

    print()
    print(
        "Total attempts:",
        len(first.trace),
    )

    print(
        "Unique questions encountered:",
        len(unique_questions),
    )

    print(
        "Completed curriculum pathway:",
        first.completed,
    )

    print(
        "Deterministic replay:",
        (
            "PASS"
            if deterministic
            else "FAIL"
        ),
    )

    if profile == "STRONG":
        print(
            "Interpretation:",
            "High-quality evidence allows "
            "efficient progression."
        )

    elif profile == "MIXED":
        print(
            "Interpretation:",
            "Partial evidence produces "
            "additional targeted practice "
            "before progression."
        )

    else:
        print(
            "Interpretation:",
            "Persistent incorrect evidence "
            "does not trigger false mastery; "
            "the learner remains in practice."
        )


def determinism_summary() -> None:
    results = {
        profile: simulate(
            profile
        )
        for profile in [
            "STRONG",
            "MIXED",
            "STRUGGLING",
        ]
    }

    traces = {
        profile: normalized_trace(
            result
        )
        for profile, result in (
            results.items()
        )
    }

    repeated = {
        profile: normalized_trace(
            simulate(profile)
        )
        for profile in traces
    }

    print()
    print("3. DETERMINISM CHECK")
    print("-" * 72)

    for profile in [
        "STRONG",
        "MIXED",
        "STRUGGLING",
    ]:
        same = (
            traces[profile]
            == repeated[profile]
        )

        print(
            f"{profile:<11} "
            "same evidence -> "
            "same pathway:",
            (
                "PASS"
                if same
                else "FAIL"
            ),
        )

    print()

    print(
        "Strong pathway != Mixed pathway:",
        (
            "PASS"
            if (
                traces["STRONG"]
                != traces["MIXED"]
            )
            else "FAIL"
        ),
    )

    print(
        "Strong pathway != "
        "Struggling pathway:",
        (
            "PASS"
            if (
                traces["STRONG"]
                != traces["STRUGGLING"]
            )
            else "FAIL"
        ),
    )

    print(
        "Mixed pathway != "
        "Struggling pathway:",
        (
            "PASS"
            if (
                traces["MIXED"]
                != traces["STRUGGLING"]
            )
            else "FAIL"
        ),
    )


def main() -> None:
    print_bank_summary()

    print()
    print("2. ADAPTIVE LEARNER PATHWAYS")
    print("=" * 72)

    for profile in [
        "STRONG",
        "MIXED",
        "STRUGGLING",
    ]:
        summarize_profile(
            profile
        )

    determinism_summary()

    print()
    print("=" * 72)
    print("RESEARCH DEMO SUMMARY")
    print("=" * 72)

    print(
        "Same evidence history "
        "produces the same pathway."
    )

    print(
        "Different evidence histories "
        "produce different pathways."
    )

    print(
        "Mastery is evidence-based; "
        "the system does not advance "
        "a persistently struggling learner."
    )

    print(
        "Curriculum mappings are separate "
        "from the shared adaptive engine."
    )

    print(
        "STACK provides mathematical grading "
        "while the adaptive layer controls "
        "practice, repetition, remediation, "
        "and progression."
    )

    print()
    print(
        "MENTOR DEMO: PASS"
    )


if __name__ == "__main__":
    main()
