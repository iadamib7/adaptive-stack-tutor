from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)


router = APIRouter(
    tags=[
        "Adaptive Interface"
    ],
)


WEB_DIR = (
    Path(__file__).resolve().parents[1]
    / "web"
)

INSTRUCTOR_HTML = (
    WEB_DIR
    / "adaptive_instructor.html"
)

STUDENT_HTML = (
    WEB_DIR
    / "adaptive_student.html"
)


@router.get(
    "/adaptive-demo",
)
def adaptive_demo() -> RedirectResponse:
    return RedirectResponse(
        url="/instructor"
    )


@router.get(
    "/instructor",
    response_class=HTMLResponse,
)
def instructor_interface() -> HTMLResponse:
    return HTMLResponse(
        INSTRUCTOR_HTML.read_text(
            encoding="utf-8"
        )
    )


@router.get(
    "/student/{session_id}",
    response_class=HTMLResponse,
)
def student_interface(
    session_id: str,
) -> HTMLResponse:
    return HTMLResponse(
        STUDENT_HTML.read_text(
            encoding="utf-8"
        )
    )
