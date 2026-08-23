from __future__ import annotations

from dataclasses import dataclass

from backend.app.content.models import (
    LicenseDecision,
)
from backend.app.content.sources.models import (
    ContentSourceDefinition,
    SourceLicensePolicy,
)


@dataclass(frozen=True)
class LicenseGateResult:
    decision: LicenseDecision
    license_code: str
    license_url: str
    attribution_required: bool
    reason: str


class ContentLicenseGate:
    """
    Convert source-level licensing policy and optional
    item-level license metadata into a repository decision.

    This does not provide legal advice. It enforces the
    platform's configured content-ingestion policy.
    """

    def evaluate(
        self,
        *,
        source: ContentSourceDefinition,
        item_license_code: str = "",
        item_license_url: str = "",
    ) -> LicenseGateResult:
        if source.policy == (
            SourceLicensePolicy.BLOCK
        ):
            return LicenseGateResult(
                decision=(
                    LicenseDecision.BLOCKED
                ),
                license_code=(
                    item_license_code
                    or source.default_license_code
                ),
                license_url=(
                    item_license_url
                    or source.default_license_url
                ),
                attribution_required=(
                    source.attribution_required
                ),
                reason=(
                    "Source policy blocks ingestion."
                ),
            )

        if source.per_item_license_required:
            if not item_license_code.strip():
                return LicenseGateResult(
                    decision=(
                        LicenseDecision.REVIEW
                    ),
                    license_code="",
                    license_url=(
                        item_license_url
                    ),
                    attribution_required=(
                        source.attribution_required
                    ),
                    reason=(
                        "This source requires an "
                        "item-level license before "
                        "content can be approved."
                    ),
                )

            return LicenseGateResult(
                decision=(
                    LicenseDecision.ALLOWED
                ),
                license_code=(
                    item_license_code
                ),
                license_url=(
                    item_license_url
                ),
                attribution_required=(
                    source.attribution_required
                ),
                reason=(
                    "Item-level license is present."
                ),
            )

        if source.policy == (
            SourceLicensePolicy.REVIEW
        ):
            return LicenseGateResult(
                decision=(
                    LicenseDecision.REVIEW
                ),
                license_code=(
                    item_license_code
                    or source.default_license_code
                ),
                license_url=(
                    item_license_url
                    or source.default_license_url
                ),
                attribution_required=(
                    source.attribution_required
                ),
                reason=(
                    "Source requires manual license "
                    "review."
                ),
            )

        license_code = (
            item_license_code
            or source.default_license_code
        )

        if not license_code.strip():
            return LicenseGateResult(
                decision=(
                    LicenseDecision.REVIEW
                ),
                license_code="",
                license_url=(
                    item_license_url
                    or source.default_license_url
                ),
                attribution_required=(
                    source.attribution_required
                ),
                reason=(
                    "No usable license code is "
                    "available."
                ),
            )

        return LicenseGateResult(
            decision=(
                LicenseDecision.ALLOWED
            ),
            license_code=license_code,
            license_url=(
                item_license_url
                or source.default_license_url
            ),
            attribution_required=(
                source.attribution_required
            ),
            reason=(
                "Source policy allows ingestion."
            ),
        )
