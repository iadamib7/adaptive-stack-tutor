import pytest

from backend.app.content.ingestion.numbas.models import (
    NumbasQuestionMetadata,
    NumbasQuestionStatus,
)
from backend.app.content.ingestion.numbas.suitability import (
    EducationalSuitability,
    NumbasSuitabilityGate,
)
from backend.app.content.models import (
    LicenseDecision,
)


KNOWN_CONCEPTS = {
    "fractions",
    "decimals",
    "percentages",
    "ratio-and-proportion",
    "algebraic-expressions",
    "linear-equations",
    "roots-and-surds",
    "probability",
}


def metadata(
    *,
    status: NumbasQuestionStatus = (
        NumbasQuestionStatus.READY
    ),
) -> NumbasQuestionMetadata:
    return NumbasQuestionMetadata(
        question_id="numbas-1",
        title="Adding fractions",
        source_url=(
            "https://numbas.example/question/1"
        ),
        project_name=(
            "Transition to university"
        ),
        status=status,
        license_code="CC-BY",
    )


def test_ready_licensed_transition_question_is_accepted() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(),
            concept_id="fractions",
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.ALLOWED
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.ACCEPT
    )

    assert (
        decision.can_enter_repository
        is True
    )


def test_unmapped_question_requires_review() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(),
            concept_id=None,
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.ALLOWED
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.REVIEW
    )


def test_unapproved_license_requires_review() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(),
            concept_id="fractions",
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.REVIEW
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.REVIEW
    )


def test_needs_testing_requires_review() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(
                status=(
                    NumbasQuestionStatus
                    .NEEDS_TESTING
                )
            ),
            concept_id="fractions",
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.ALLOWED
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.REVIEW
    )


def test_has_problems_requires_review() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(
                status=(
                    NumbasQuestionStatus
                    .HAS_PROBLEMS
                )
            ),
            concept_id="fractions",
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.ALLOWED
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.REVIEW
    )


def test_should_not_use_is_rejected() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(
                status=(
                    NumbasQuestionStatus
                    .SHOULD_NOT_USE
                )
            ),
            concept_id="fractions",
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.ALLOWED
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.REJECT
    )


def test_broken_question_is_rejected() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(
                status=(
                    NumbasQuestionStatus
                    .DOES_NOT_WORK
                )
            ),
            concept_id="fractions",
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.ALLOWED
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.REJECT
    )


def test_out_of_graph_concept_is_rejected() -> None:
    decision = (
        NumbasSuitabilityGate()
        .evaluate(
            metadata=metadata(),
            concept_id="multivariable-calculus",
            known_transition_concept_ids=(
                KNOWN_CONCEPTS
            ),
            license_decision=(
                LicenseDecision.ALLOWED
            ),
        )
    )

    assert decision.decision == (
        EducationalSuitability.REJECT
    )


def test_empty_question_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="question_id",
    ):
        NumbasQuestionMetadata(
            question_id=" ",
            title="Question",
            source_url="https://example.com",
            project_name="Project",
        )
