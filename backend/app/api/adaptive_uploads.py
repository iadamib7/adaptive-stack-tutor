from __future__ import annotations

import json

from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from backend.app.api.adaptive_sessions import (
    _build_response,
    _sessions,
)

from backend.app.integrations.stack_api.http_client import (
    HttpStackEvaluationClient,
)

from backend.app.learning.adaptive_engine.document_import import (
    AdaptiveDocumentImporter,
)

from backend.app.learning.adaptive_engine.historical_responses import (
    HistoricalStackResponseImporter,
)

from backend.app.learning.adaptive_engine.session_service import (
    GenericAdaptiveSessionService,
)

from backend.app.learning.adaptive_engine.stack_runtime import (
    AdaptiveStackRenderer,
)


router = APIRouter(
    prefix="/api/adaptive/uploads",
    tags=["adaptive uploads"],
)


SUPPORTED_EXTENSIONS = {
    ".xml",
    ".xlsx",
    ".xlsm",
    ".csv",
    ".docx",
    ".pdf",
}


def _merge_metadata(
    *,
    generated_json: str | None,
    instructor_json: str | None,
) -> str | None:
    """
    Merge generated document metadata with optional
    instructor-provided metadata.

    Instructor values take precedence.
    """

    if (
        not generated_json
        and not instructor_json
    ):
        return None

    generated: dict[str, object] = {
        "questions": {}
    }

    instructor: dict[str, object] = {
        "questions": {}
    }

    if generated_json:
        try:
            loaded = json.loads(
                generated_json
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                "Generated adaptive metadata "
                "is invalid JSON."
            ) from error

        if not isinstance(
            loaded,
            dict,
        ):
            raise ValueError(
                "Generated adaptive metadata "
                "must be a JSON object."
            )

        generated = loaded

    if instructor_json:
        try:
            loaded = json.loads(
                instructor_json
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                "Uploaded adaptive metadata "
                "is invalid JSON."
            ) from error

        if not isinstance(
            loaded,
            dict,
        ):
            raise ValueError(
                "Uploaded adaptive metadata "
                "must be a JSON object."
            )

        instructor = loaded

    generated_questions = (
        generated.get(
            "questions",
            {},
        )
    )

    instructor_questions = (
        instructor.get(
            "questions",
            {},
        )
    )

    if not isinstance(
        generated_questions,
        dict,
    ):
        raise ValueError(
            "Generated metadata "
            "'questions' must be an object."
        )

    if not isinstance(
        instructor_questions,
        dict,
    ):
        raise ValueError(
            "Uploaded metadata "
            "'questions' must be an object."
        )

    merged_questions: dict[
        str,
        object,
    ] = {}

    for (
        question_id,
        metadata,
    ) in generated_questions.items():
        if not isinstance(
            question_id,
            str,
        ):
            continue

        merged_questions[
            question_id
        ] = metadata

    for (
        question_id,
        metadata,
    ) in instructor_questions.items():
        if not isinstance(
            question_id,
            str,
        ):
            continue

        existing = (
            merged_questions.get(
                question_id
            )
        )

        if (
            isinstance(
                existing,
                dict,
            )
            and isinstance(
                metadata,
                dict,
            )
        ):
            combined = dict(
                existing
            )

            combined.update(
                metadata
            )

            merged_questions[
                question_id
            ] = combined

        else:
            merged_questions[
                question_id
            ] = metadata

    return json.dumps(
        {
            "questions":
                merged_questions
        }
    )


def _build_service(
    *,
    xml_text: str,
    metadata_json: str | None,
) -> GenericAdaptiveSessionService:
    return (
        GenericAdaptiveSessionService
        .from_xml(
            xml_text=xml_text,
            metadata_json=(
                metadata_json
            ),
            evaluation_client=(
                HttpStackEvaluationClient()
            ),
            renderer=(
                AdaptiveStackRenderer()
            ),
        )
    )


def _historical_summary(
    *,
    filename: str,
    content: bytes,
) -> dict[
    str,
    object,
]:
    dataset = (
        HistoricalStackResponseImporter()
        .import_bytes(
            filename=filename,
            content=content,
        )
    )

    items: list[
        dict[str, object]
    ] = []

    for item in dataset.item_statistics:
        items.append(
            {
                "question_number":
                    item.question_number,
                "attempt_count":
                    item.attempt_count,
                "mean_score":
                    item.mean_score,
                "full_credit_rate":
                    item.full_credit_rate,
                "zero_credit_rate":
                    item.zero_credit_rate,
                "unique_seeds":
                    item.unique_seeds,
                "prt_outcomes": [
                    {
                        "outcome":
                            outcome,
                        "count":
                            count,
                    }
                    for (
                        outcome,
                        count,
                    )
                    in item.prt_outcome_counts
                ],
            }
        )

    return {
        "kind":
            "historical_analysis",
        "filename":
            filename,
        "attempt_count":
            dataset.attempt_count,
        "question_count":
            dataset.question_count,
        "items":
            items,
    }


def _looks_like_historical_csv(
    content: bytes,
) -> bool:
    try:
        text = content.decode(
            "utf-8-sig"
        )
    except UnicodeDecodeError:
        return False

    first_line = (
        text.splitlines()[0]
        if text.splitlines()
        else ""
    )

    lowered = (
        first_line.lower()
    )

    return (
        "question 1" in lowered
        and "response 1" in lowered
        and "right answer 1" in lowered
    )


@router.post(
    "/sessions",
)
async def create_uploaded_adaptive_session(
    learner_id: int = Form(...),
    question_bank: UploadFile = File(...),
    metadata_file: (
        UploadFile | None
    ) = File(None),
    metadata_json: (
        str | None
    ) = Form(None),
) -> dict[
    str,
    object,
]:
    """
    Accept either:

    1. an instructor question source, or
    2. a historical STACK response CSV.

    Historical response CSV files are analyzed.
    They do not start a learner session.
    """

    filename = (
        question_bank.filename
        or ""
    )

    suffix = Path(
        filename
    ).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported question-bank "
                "format. Upload .xml, .xlsx, "
                ".xlsm, .csv, .docx, or .pdf."
            ),
        )

    try:
        content = await (
            question_bank.read()
        )

        if not content:
            raise ValueError(
                "Uploaded file is empty."
            )

        # ----------------------------------------
        # STACK historical response CSV
        # ----------------------------------------

        if (
            suffix == ".csv"
            and _looks_like_historical_csv(
                content
            )
        ):
            return _historical_summary(
                filename=filename,
                content=content,
            )

        # ----------------------------------------
        # Optional adaptive metadata
        # ----------------------------------------

        uploaded_metadata_text = (
            metadata_json.strip()
            if (
                metadata_json
                and metadata_json.strip()
            )
            else None
        )

        if metadata_file is not None:
            metadata_content = await (
                metadata_file.read()
            )

            if metadata_content:
                try:
                    file_metadata = (
                        metadata_content.decode(
                            "utf-8"
                        )
                    )
                except UnicodeDecodeError as error:
                    raise ValueError(
                        "Adaptive metadata file "
                        "must be UTF-8 JSON."
                    ) from error

                if uploaded_metadata_text:
                    uploaded_metadata_text = (
                        _merge_metadata(
                            generated_json=(
                                uploaded_metadata_text
                            ),
                            instructor_json=(
                                file_metadata
                            ),
                        )
                    )

                else:
                    uploaded_metadata_text = (
                        file_metadata
                    )

        # ----------------------------------------
        # Native STACK XML
        # ----------------------------------------

        if suffix == ".xml":
            try:
                xml_text = (
                    content.decode(
                        "utf-8"
                    )
                )
            except UnicodeDecodeError as error:
                raise ValueError(
                    "XML question bank "
                    "must be UTF-8."
                ) from error

            final_metadata = (
                uploaded_metadata_text
            )

        # ----------------------------------------
        # XLSX / XLSM / CSV / DOCX / PDF
        # ----------------------------------------

        else:
            converted = (
                AdaptiveDocumentImporter()
                .import_bytes(
                    filename=filename,
                    content=content,
                )
            )

            xml_text = (
                converted
                .question_bank_xml
            )

            final_metadata = (
                _merge_metadata(
                    generated_json=(
                        converted
                        .metadata_json
                    ),
                    instructor_json=(
                        uploaded_metadata_text
                    ),
                )
            )

        # ----------------------------------------
        # Same adaptive engine for all question
        # source formats.
        # ----------------------------------------

        service = _build_service(
            xml_text=xml_text,
            metadata_json=(
                final_metadata
            ),
        )

        view = service.start(
            learner_id=learner_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    session_id = str(
        uuid4()
    )

    _sessions[
        session_id
    ] = service

    response = _build_response(
        session_id=session_id,
        view=view,
    )

    payload = response.model_dump()

    payload[
        "kind"
    ] = "adaptive_session"

    return payload


@router.get(
    "/health"
)
def adaptive_upload_health() -> dict[
    str,
    object,
]:
    return {
        "status": "healthy",
        "supported_formats": [
            ".xml",
            ".xlsx",
            ".xlsm",
            ".csv",
            ".docx",
            ".pdf",
        ],
    }
