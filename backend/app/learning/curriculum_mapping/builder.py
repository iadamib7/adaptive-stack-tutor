from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_question(
    question_id: str,
    question_name: str,
    role: str,
    sequence_order: int,
    required_for_mastery: bool,
    notes: str,
) -> dict[str, Any]:
    return {
        "question_id": question_id,
        "question_name": question_name,
        "source_profile_id": (
            "kenya-grade9-development"
        ),
        "source_file": "grade9_questions.xml",
        "role": role,
        "sequence_order": sequence_order,
        "required_for_mastery": (
            required_for_mastery
        ),
        "notes": notes,
    }


def build_integer_operations() -> dict[str, Any]:
    return {
        "concept_id": "KE-G9-INTEGER-OPERATIONS",
        "concept_name": "Integer Operations",
        "curriculum_profile_id": (
            "kenya-grade9-development"
        ),
        "level_id": "KE-G9",
        "strand": "Whole Numbers",
        "sub_strand": "Integers",
        "learning_outcome": (
            "Demonstrate understanding of addition, "
            "subtraction, multiplication, division, "
            "and combined operations involving integers."
        ),
        "prerequisite_concept_ids": [],
        "next_concept_ids": [
            "KE-G9-INDICES-EXPONENTS"
        ],
        "questions": [
            build_question(
                question_id="207582",
                question_name=(
                    "Addition of integers (cupcakes)"
                ),
                role="foundation",
                sequence_order=1,
                required_for_mastery=False,
                notes=(
                    "Provides evidence of basic "
                    "integer addition."
                ),
            ),
            build_question(
                question_id="207596",
                question_name=(
                    "Subtraction of integers"
                ),
                role="foundation",
                sequence_order=2,
                required_for_mastery=False,
                notes=(
                    "Provides evidence of basic "
                    "integer subtraction."
                ),
            ),
            build_question(
                question_id="207591",
                question_name=(
                    "Multiplication of integers"
                ),
                role="practice",
                sequence_order=3,
                required_for_mastery=False,
                notes=(
                    "Provides evidence of integer "
                    "multiplication."
                ),
            ),
            build_question(
                question_id="207589",
                question_name=(
                    "Division of integers (apples)"
                ),
                role="practice",
                sequence_order=4,
                required_for_mastery=False,
                notes=(
                    "Provides evidence of integer "
                    "division."
                ),
            ),
            build_question(
                question_id="207630",
                question_name=(
                    "Combined operations of integers"
                ),
                role="mastery_check",
                sequence_order=5,
                required_for_mastery=True,
                notes=(
                    "Integrated integer-operations "
                    "mastery check."
                ),
            ),
        ],
        "mapping_status": "review_required",
        "source_basis": (
            "STACK Grade 9 Whole Numbers > Integers."
        ),
        "reviewer_notes": (
            "Existing learner-flow mapping retained."
        ),
    }


def build_indices_and_exponents() -> dict[str, Any]:
    return {
        "concept_id": "KE-G9-INDICES-EXPONENTS",
        "concept_name": "Indices and Exponents",
        "curriculum_profile_id": (
            "kenya-grade9-development"
        ),
        "level_id": "KE-G9",
        "strand": "Whole Numbers",
        "sub_strand": "Indices and Logarithms",
        "learning_outcome": (
            "Apply index laws to represent and simplify "
            "numbers and algebraic expressions."
        ),
        "prerequisite_concept_ids": [
            "KE-G9-INTEGER-OPERATIONS"
        ],
        "next_concept_ids": [
            "ratio-and-proportion"
        ],
        "questions": [
            build_question(
                question_id="206793",
                question_name=(
                    "Expressing numbers in index form"
                ),
                role="foundation",
                sequence_order=1,
                required_for_mastery=False,
                notes=(
                    "Introduces representation using "
                    "index notation."
                ),
            ),
            build_question(
                question_id="206819",
                question_name=(
                    "Writing numbers in simplest "
                    "index form as a product"
                ),
                role="foundation",
                sequence_order=2,
                required_for_mastery=False,
                notes=(
                    "Simplifying index-form "
                    "expressions."
                ),
            ),
            build_question(
                question_id="206873",
                question_name=(
                    "Writing numbers as a single "
                    "power of a prime"
                ),
                role="practice",
                sequence_order=3,
                required_for_mastery=False,
                notes=(
                    "Assesses prime-power "
                    "representation."
                ),
            ),
            build_question(
                question_id="207419",
                question_name=(
                    "Applying the Zero Exponent Law"
                ),
                role="practice",
                sequence_order=4,
                required_for_mastery=False,
                notes=(
                    "Practice with the zero "
                    "exponent law."
                ),
            ),
            build_question(
                question_id="207420",
                question_name=(
                    "Applying negative index rules"
                ),
                role="practice",
                sequence_order=5,
                required_for_mastery=False,
                notes=(
                    "Practice applying negative "
                    "index rules."
                ),
            ),
            build_question(
                question_id="206946",
                question_name=(
                    "Using multiplicative, divisive, "
                    "and bracket laws of indices"
                ),
                role="mastery_check",
                sequence_order=6,
                required_for_mastery=True,
                notes=(
                    "Integrated index-laws "
                    "mastery check."
                ),
            ),
        ],
        "mapping_status": "review_required",
        "source_basis": (
            "STACK Grade 9 Indices and Logarithms."
        ),
        "reviewer_notes": (
            "Existing learner-flow mapping retained "
            "and linked to expanded practice content."
        ),
    }


def build_ratio_and_proportion() -> dict[str, Any]:
    return {
        "concept_id": "ratio-and-proportion",
        "concept_name": "Ratio and Proportion",
        "curriculum_profile_id": (
            "kenya-grade9-development"
        ),
        "level_id": "G9-G10",
        "strand": "Number",
        "sub_strand": "Ratio and Proportion",
        "learning_outcome": (
            "Use ratios and proportional reasoning "
            "to solve numerical and contextual problems."
        ),
        "prerequisite_concept_ids": [],
        "next_concept_ids": [
            "coordinate-graphs"
        ],
        "questions": [
            build_question(
                question_id="207616",
                question_name=(
                    "Using ratios to determine the "
                    "number of boys in a class"
                ),
                role="foundation",
                sequence_order=1,
                required_for_mastery=False,
                notes=(
                    "Introductory contextual ratio problem."
                ),
            ),
            build_question(
                question_id="207646",
                question_name=(
                    "Relating different ratios from "
                    "a given statement"
                ),
                role="practice",
                sequence_order=2,
                required_for_mastery=False,
                notes=(
                    "Provides additional ratio "
                    "relationship practice."
                ),
            ),
            build_question(
                question_id="207534",
                question_name=(
                    "Finding the unknown number in "
                    "a continuous proportion"
                ),
                role="practice",
                sequence_order=3,
                required_for_mastery=False,
                notes=(
                    "Develops proportional equation "
                    "reasoning."
                ),
            ),
            build_question(
                question_id="207542",
                question_name=(
                    "Finding the number of days taken "
                    "by a given number of men"
                ),
                role="mastery_check",
                sequence_order=4,
                required_for_mastery=True,
                notes=(
                    "Contextual compound-proportion "
                    "mastery check."
                ),
            ),
        ],
        "mapping_status": "review_required",
        "source_basis": (
            "STACK Grade 9 Compound Proportion."
        ),
        "reviewer_notes": (
            "Initial expanded practice mapping."
        ),
    }


def build_coordinate_graphs() -> dict[str, Any]:
    return {
        "concept_id": "coordinate-graphs",
        "concept_name": (
            "Coordinates and Linear Graphs"
        ),
        "curriculum_profile_id": (
            "kenya-grade9-development"
        ),
        "level_id": "G9-G10",
        "strand": "Geometry and Algebra",
        "sub_strand": (
            "Coordinates and Graphs"
        ),
        "learning_outcome": (
            "Interpret coordinates, plot points, "
            "sketch straight-line graphs, and "
            "determine equations of lines."
        ),
        "prerequisite_concept_ids": [],
        "next_concept_ids": [
            "similarity"
        ],
        "questions": [
            build_question(
                question_id="206939",
                question_name=(
                    "Writing down coordinates of "
                    "points in a graph"
                ),
                role="foundation",
                sequence_order=1,
                required_for_mastery=False,
                notes=(
                    "Foundation coordinate-reading "
                    "practice."
                ),
            ),
            build_question(
                question_id="206961",
                question_name=(
                    "Plotting points on a "
                    "Cartesian plane"
                ),
                role="practice",
                sequence_order=2,
                required_for_mastery=False,
                notes=(
                    "Interactive coordinate plotting."
                ),
            ),
            build_question(
                question_id="207067",
                question_name=(
                    "Sketching straight-line graphs "
                    "y = mx + c"
                ),
                role="practice",
                sequence_order=3,
                required_for_mastery=False,
                notes=(
                    "Straight-line graph practice."
                ),
            ),
            build_question(
                question_id="207059",
                question_name=(
                    "Determining the equation of "
                    "a straight line"
                ),
                role="mastery_check",
                sequence_order=4,
                required_for_mastery=True,
                notes=(
                    "Integrated linear-graph "
                    "mastery check."
                ),
            ),
        ],
        "mapping_status": "review_required",
        "source_basis": (
            "STACK Grade 9 Geometry > Coordinates "
            "and Graphs."
        ),
        "reviewer_notes": (
            "Initial expanded practice mapping."
        ),
    }


def build_similarity() -> dict[str, Any]:
    return {
        "concept_id": "similarity",
        "concept_name": "Similarity and Scale",
        "curriculum_profile_id": (
            "kenya-grade9-development"
        ),
        "level_id": "G9-G10",
        "strand": "Geometry",
        "sub_strand": (
            "Similarity and Enlargement"
        ),
        "learning_outcome": (
            "Identify similar figures and determine "
            "linear scale factors."
        ),
        "prerequisite_concept_ids": [
            "ratio-and-proportion"
        ],
        "next_concept_ids": [
            "trigonometry"
        ],
        "questions": [
            build_question(
                question_id="221322",
                question_name=(
                    "Determining similar figures"
                ),
                role="foundation",
                sequence_order=1,
                required_for_mastery=False,
                notes=(
                    "Introduces identification of "
                    "similar figures."
                ),
            ),
            build_question(
                question_id="221366",
                question_name=(
                    "Determining the linear "
                    "scale factor"
                ),
                role="mastery_check",
                sequence_order=2,
                required_for_mastery=True,
                notes=(
                    "Checks understanding of "
                    "linear scale factor."
                ),
            ),
        ],
        "mapping_status": "review_required",
        "source_basis": (
            "STACK Grade 9 Geometry > Similarity "
            "and Enlargement."
        ),
        "reviewer_notes": (
            "Initial expanded practice mapping."
        ),
    }


def build_trigonometry() -> dict[str, Any]:
    return {
        "concept_id": "trigonometry",
        "concept_name": (
            "Introductory Trigonometry"
        ),
        "curriculum_profile_id": (
            "kenya-grade9-development"
        ),
        "level_id": "G9-G10",
        "strand": "Geometry",
        "sub_strand": "Trigonometry",
        "learning_outcome": (
            "Identify sides of right-angled triangles, "
            "use trigonometric ratios, and determine "
            "unknown sides and angles."
        ),
        "prerequisite_concept_ids": [
            "similarity"
        ],
        "next_concept_ids": [],
        "questions": [
            build_question(
                question_id="221194",
                question_name=(
                    "Identifying sides of a "
                    "right-angled triangle"
                ),
                role="foundation",
                sequence_order=1,
                required_for_mastery=False,
                notes=(
                    "Foundation vocabulary for "
                    "right-triangle trigonometry."
                ),
            ),
            build_question(
                question_id="221196",
                question_name=(
                    "Determining sine, cosine and "
                    "tangent of an angle"
                ),
                role="practice",
                sequence_order=2,
                required_for_mastery=False,
                notes=(
                    "Introduces the three basic "
                    "trigonometric ratios."
                ),
            ),
            build_question(
                question_id="221209",
                question_name=(
                    "Calculating sines, cosines "
                    "and tangents using a calculator"
                ),
                role="practice",
                sequence_order=3,
                required_for_mastery=False,
                notes=(
                    "Calculator-based ratio practice."
                ),
            ),
            build_question(
                question_id="221908",
                question_name=(
                    "Finding an unknown angle using "
                    "a trigonometric ratio"
                ),
                role="practice",
                sequence_order=4,
                required_for_mastery=False,
                notes=(
                    "Applies inverse trigonometric "
                    "reasoning."
                ),
            ),
            build_question(
                question_id="221909",
                question_name=(
                    "Calculating the length of a "
                    "right-angled triangle"
                ),
                role="mastery_check",
                sequence_order=5,
                required_for_mastery=True,
                notes=(
                    "Integrated right-triangle "
                    "trigonometry mastery check."
                ),
            ),
        ],
        "mapping_status": "review_required",
        "source_basis": (
            "STACK Grade 9 Geometry > Trigonometry."
        ),
        "reviewer_notes": (
            "Introductory trigonometry only. "
            "Trigonometric-equation item 222191 "
            "is intentionally excluded."
        ),
    }


def build_default_curriculum() -> dict[str, Any]:
    return {
        "version": "0.4",
        "name": (
            "Grade 9 to Grade 10 Adaptive "
            "Mathematics Practice Map"
        ),
        "intended_context": (
            "Adaptive mathematics practice supporting "
            "the Grade 9 to Grade 10 transition."
        ),
        "development_context": (
            "Expanded using validated questions from "
            "the existing Innodems STACK Grade 9 "
            "question bank."
        ),
        "mappings": [
            build_integer_operations(),
            build_indices_and_exponents(),
            build_ratio_and_proportion(),
            build_coordinate_graphs(),
            build_similarity(),
            build_trigonometry(),
        ],
    }


def write_curriculum(
    output_path: Path,
) -> Path:
    curriculum = build_default_curriculum()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            curriculum,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path