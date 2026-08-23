import pytest

from backend.app.content.ingestion.concept_mapping_models import (
    ConceptMappingDecision,
    MappingConfidence,
    MappingStatus,
)
from backend.app.content.ingestion.converter import (
    ContentConversionError,
    ImportedContentConverter,
)
from backend.app.content.ingestion.models import (
    ImportedContentRecord,
)
from backend.app.content.models import (
    ContentKind,
    ContentSource,
    LicenseDecision,
)


def record(
    *,
    external_id: str = "1001",
    provider: str = "stack",
) -> ImportedContentRecord:
    return ImportedContentRecord(
        source_provider=provider,
        source_reference="questions.xml",
        external_id=external_id,
        title="Test question",
        category_path=(
            "Grade 9 / Integers"
        ),
        input_names=(
            "ans1",
        ),
        prt_names=(
            "prt1",
        ),
        deployed_seeds=(
            10,
            20,
        ),
    )


def mapped(
    *,
    external_id: str = "1001",
) -> ConceptMappingDecision:
    return ConceptMappingDecision(
        external_id=external_id,
        concept_id=(
            "integer-operations"
        ),
        status=MappingStatus.MAPPED,
        confidence=(
            MappingConfidence.HIGH
        ),
        reason="Test mapping.",
        matched_rule="integers",
    )


def test_stack_record_converts() -> None:
    item = (
        ImportedContentConverter()
        .convert(
            record=record(),
            mapping=mapped(),
        )
    )

    assert item.content_id == (
        "stack:1001"
    )

    assert item.concept_id == (
        "integer-operations"
    )

    assert item.kind == (
        ContentKind.QUESTION
    )

    assert item.source == (
        ContentSource.STACK
    )


def test_external_stack_content_requires_license_review() -> None:
    item = (
        ImportedContentConverter()
        .convert(
            record=record(),
            mapping=mapped(),
        )
    )

    assert item.license_decision == (
        LicenseDecision.REVIEW
    )

    assert item.can_be_delivered is False


def test_seeded_stack_question_gets_variant_group() -> None:
    item = (
        ImportedContentConverter()
        .convert(
            record=record(),
            mapping=mapped(),
        )
    )

    assert item.variant_group_id == (
        "stack:1001"
    )


def test_conversion_preserves_audit_metadata() -> None:
    item = (
        ImportedContentConverter()
        .convert(
            record=record(),
            mapping=mapped(),
        )
    )

    metadata = dict(
        item.metadata
    )

    assert metadata[
        "external_id"
    ] == "1001"

    assert metadata[
        "input_count"
    ] == "1"

    assert metadata[
        "prt_count"
    ] == "1"

    assert metadata[
        "mapping_rule"
    ] == "integers"


def test_unmapped_record_cannot_be_converted() -> None:
    decision = ConceptMappingDecision(
        external_id="1001",
        concept_id=None,
        status=(
            MappingStatus.UNMAPPED
        ),
        confidence=(
            MappingConfidence.LOW
        ),
        reason="No mapping.",
    )

    with pytest.raises(
        ContentConversionError,
        match="approved concept mapping",
    ):
        ImportedContentConverter().convert(
            record=record(),
            mapping=decision,
        )


def test_mismatched_ids_are_rejected() -> None:
    with pytest.raises(
        ContentConversionError,
        match="different external IDs",
    ):
        ImportedContentConverter().convert(
            record=record(
                external_id="1001"
            ),
            mapping=mapped(
                external_id="9999"
            ),
        )


def test_convert_many_skips_unmapped_content() -> None:
    records = [
        record(
            external_id="1001"
        ),
        record(
            external_id="1002"
        ),
    ]

    mappings = [
        mapped(
            external_id="1001"
        ),
        ConceptMappingDecision(
            external_id="1002",
            concept_id=None,
            status=(
                MappingStatus.UNMAPPED
            ),
            confidence=(
                MappingConfidence.LOW
            ),
            reason="No mapping.",
        ),
    ]

    items = (
        ImportedContentConverter()
        .convert_many(
            records=records,
            mappings=mappings,
        )
    )

    assert [
        item.content_id
        for item in items
    ] == [
        "stack:1001"
    ]


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(
        ContentConversionError,
        match="Unsupported content provider",
    ):
        ImportedContentConverter().convert(
            record=record(
                provider="mystery"
            ),
            mapping=mapped(),
        )
