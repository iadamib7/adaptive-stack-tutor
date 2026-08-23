import pytest

from backend.app.content.sources.default_registry import (
    DEFAULT_CONTENT_SOURCE_REGISTRY,
)
from backend.app.content.sources.license_gate import (
    ContentLicenseGate,
)
from backend.app.content.sources.models import (
    ContentSourceDefinition,
    SourceLicensePolicy,
)
from backend.app.content.sources.registry import (
    ContentSourceRegistry,
)
from backend.app.content.models import (
    LicenseDecision,
)


def source(
    *,
    source_id: str = "test",
    policy: SourceLicensePolicy = (
        SourceLicensePolicy.ALLOW
    ),
    license_code: str = "CC-BY",
    per_item: bool = False,
) -> ContentSourceDefinition:
    return ContentSourceDefinition(
        source_id=source_id,
        provider="test",
        display_name="Test source",
        default_license_code=(
            license_code
        ),
        per_item_license_required=(
            per_item
        ),
        policy=policy,
    )


def test_registry_returns_known_source() -> None:
    registry = ContentSourceRegistry(
        [
            source()
        ]
    )

    assert (
        registry.require("test")
        .provider
        == "test"
    )


def test_duplicate_source_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        ContentSourceRegistry(
            [
                source(),
                source(),
            ]
        )


def test_allow_policy_can_approve_content() -> None:
    result = ContentLicenseGate().evaluate(
        source=source()
    )

    assert result.decision == (
        LicenseDecision.ALLOWED
    )


def test_block_policy_blocks_content() -> None:
    result = ContentLicenseGate().evaluate(
        source=source(
            policy=(
                SourceLicensePolicy.BLOCK
            )
        )
    )

    assert result.decision == (
        LicenseDecision.BLOCKED
    )


def test_review_policy_requires_review() -> None:
    result = ContentLicenseGate().evaluate(
        source=source(
            policy=(
                SourceLicensePolicy.REVIEW
            )
        )
    )

    assert result.decision == (
        LicenseDecision.REVIEW
    )


def test_per_item_license_missing_requires_review() -> None:
    result = ContentLicenseGate().evaluate(
        source=source(
            license_code="",
            per_item=True,
        )
    )

    assert result.decision == (
        LicenseDecision.REVIEW
    )


def test_per_item_license_can_approve_item() -> None:
    result = ContentLicenseGate().evaluate(
        source=source(
            license_code="",
            per_item=True,
        ),
        item_license_code=(
            "CC-BY-4.0"
        ),
    )

    assert result.decision == (
        LicenseDecision.ALLOWED
    )

    assert result.license_code == (
        "CC-BY-4.0"
    )


def test_numbas_cc_by_is_initially_allowed() -> None:
    source_definition = (
        DEFAULT_CONTENT_SOURCE_REGISTRY
        .require(
            "numbas-cc-by"
        )
    )

    result = ContentLicenseGate().evaluate(
        source=source_definition
    )

    assert result.decision == (
        LicenseDecision.ALLOWED
    )


def test_openstax_requires_item_license() -> None:
    source_definition = (
        DEFAULT_CONTENT_SOURCE_REGISTRY
        .require(
            "openstax"
        )
    )

    result = ContentLicenseGate().evaluate(
        source=source_definition
    )

    assert result.decision == (
        LicenseDecision.REVIEW
    )


def test_khan_content_is_blocked() -> None:
    source_definition = (
        DEFAULT_CONTENT_SOURCE_REGISTRY
        .require(
            "khan-academy"
        )
    )

    result = ContentLicenseGate().evaluate(
        source=source_definition
    )

    assert result.decision == (
        LicenseDecision.BLOCKED
    )
