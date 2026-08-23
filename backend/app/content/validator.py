from __future__ import annotations

from dataclasses import dataclass

from backend.app.content.models import (
    ContentSource,
    LearningContentItem,
    LicenseDecision,
)


@dataclass(frozen=True)
class ContentRepositoryValidationError:
    code: str
    message: str
    content_id: str | None = None


class LearningContentValidator:
    """
    Validate educational and repository-level invariants.

    This validator does not decide copyright law.
    License decisions must be supplied by the content
    ingestion/review process.
    """

    def validate(
        self,
        *,
        items: list[
            LearningContentItem
        ],
        known_concept_ids: set[str],
    ) -> list[
        ContentRepositoryValidationError
    ]:
        errors: list[
            ContentRepositoryValidationError
        ] = []

        seen_ids: set[str] = set()

        for item in items:
            if item.content_id in seen_ids:
                errors.append(
                    ContentRepositoryValidationError(
                        code="duplicate_content",
                        message=(
                            "Duplicate content ID: "
                            f"{item.content_id}"
                        ),
                        content_id=(
                            item.content_id
                        ),
                    )
                )
            else:
                seen_ids.add(
                    item.content_id
                )

            if (
                item.concept_id
                not in known_concept_ids
            ):
                errors.append(
                    ContentRepositoryValidationError(
                        code="unknown_concept",
                        message=(
                            f"{item.content_id} "
                            "references unknown concept "
                            f"{item.concept_id}."
                        ),
                        content_id=(
                            item.content_id
                        ),
                    )
                )

            for prerequisite_id in (
                item.prerequisite_concept_ids
            ):
                if (
                    prerequisite_id
                    not in known_concept_ids
                ):
                    errors.append(
                        ContentRepositoryValidationError(
                            code=(
                                "unknown_prerequisite"
                            ),
                            message=(
                                f"{item.content_id} "
                                "references unknown "
                                "prerequisite concept "
                                f"{prerequisite_id}."
                            ),
                            content_id=(
                                item.content_id
                            ),
                        )
                    )

            if (
                item.source
                not in {
                    ContentSource.INTERNAL,
                    ContentSource.GENERATED,
                }
                and not item.source_reference.strip()
            ):
                errors.append(
                    ContentRepositoryValidationError(
                        code=(
                            "missing_source_reference"
                        ),
                        message=(
                            f"{item.content_id} "
                            "has no source reference."
                        ),
                        content_id=(
                            item.content_id
                        ),
                    )
                )

            if (
                item.license_decision
                == LicenseDecision.ALLOWED
                and not item.license_code.strip()
            ):
                errors.append(
                    ContentRepositoryValidationError(
                        code=(
                            "missing_license"
                        ),
                        message=(
                            f"{item.content_id} "
                            "is marked deliverable but "
                            "has no license code."
                        ),
                        content_id=(
                            item.content_id
                        ),
                    )
                )

        return errors

    def require_valid(
        self,
        *,
        items: list[
            LearningContentItem
        ],
        known_concept_ids: set[str],
    ) -> None:
        errors = self.validate(
            items=items,
            known_concept_ids=(
                known_concept_ids
            ),
        )

        if not errors:
            return

        message = "; ".join(
            error.message
            for error in errors
        )

        raise ValueError(
            "Invalid learning content repository: "
            + message
        )
