from backend.app.content.sources.models import (
    ContentSourceDefinition,
    SourceLicensePolicy,
)
from backend.app.content.sources.registry import (
    ContentSourceRegistry,
)


DEFAULT_CONTENT_SOURCE_REGISTRY = (
    ContentSourceRegistry(
        [
            ContentSourceDefinition(
                source_id="internal",
                provider="internal",
                display_name=(
                    "Internal authored content"
                ),
                default_license_code=(
                    "INTERNAL"
                ),
                policy=(
                    SourceLicensePolicy.ALLOW
                ),
            ),
            ContentSourceDefinition(
                source_id="generated",
                provider="generated",
                display_name=(
                    "Platform-generated content"
                ),
                default_license_code=(
                    "INTERNAL-GENERATED"
                ),
                policy=(
                    SourceLicensePolicy.ALLOW
                ),
            ),
            ContentSourceDefinition(
                source_id="stack-local",
                provider="stack",
                display_name=(
                    "Current STACK development bank"
                ),
                per_item_license_required=True,
                policy=(
                    SourceLicensePolicy.REVIEW
                ),
                notes=(
                    "Existing development content. "
                    "License must be verified before "
                    "new-repository delivery."
                ),
            ),
            ContentSourceDefinition(
                source_id="numbas-cc-by",
                provider="numbas",
                display_name=(
                    "Numbas CC BY content"
                ),
                default_license_code=(
                    "CC-BY"
                ),
                attribution_required=True,
                commercial_use_allowed=True,
                policy=(
                    SourceLicensePolicy.ALLOW
                ),
            ),
            ContentSourceDefinition(
                source_id="numbas-noncommercial",
                provider="numbas",
                display_name=(
                    "Numbas non-commercial content"
                ),
                attribution_required=True,
                commercial_use_allowed=False,
                policy=(
                    SourceLicensePolicy.REVIEW
                ),
            ),
            ContentSourceDefinition(
                source_id="openstax",
                provider="openstax",
                display_name=(
                    "OpenStax Exercises"
                ),
                attribution_required=True,
                per_item_license_required=True,
                policy=(
                    SourceLicensePolicy.REVIEW
                ),
            ),
            ContentSourceDefinition(
                source_id="khan-academy",
                provider="khan",
                display_name=(
                    "Khan Academy"
                ),
                policy=(
                    SourceLicensePolicy.BLOCK
                ),
                notes=(
                    "Do not ingest learner content "
                    "into this platform."
                ),
            ),
            ContentSourceDefinition(
                source_id="unknown-web",
                provider="web",
                display_name=(
                    "Unknown web source"
                ),
                policy=(
                    SourceLicensePolicy.BLOCK
                ),
            ),
        ]
    )
)
