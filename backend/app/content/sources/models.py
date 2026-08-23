from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SourceLicensePolicy(
    str,
    Enum,
):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


@dataclass(frozen=True)
class ContentSourceDefinition:
    source_id: str
    provider: str
    display_name: str

    default_license_code: str = ""
    default_license_url: str = ""

    attribution_required: bool = False
    share_alike_required: bool = False
    commercial_use_allowed: bool | None = None

    per_item_license_required: bool = False

    policy: SourceLicensePolicy = (
        SourceLicensePolicy.REVIEW
    )

    notes: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError(
                "source_id must not be empty."
            )

        if not self.provider.strip():
            raise ValueError(
                "provider must not be empty."
            )

        if not self.display_name.strip():
            raise ValueError(
                "display_name must not be empty."
            )
