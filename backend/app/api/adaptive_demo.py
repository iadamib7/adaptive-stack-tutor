from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(
    tags=[
        "Adaptive Demo"
    ],
)


HTML_FILE = (
    Path(__file__).resolve().parents[1]
    / "web"
    / "adaptive_demo.html"
)


@router.get(
    "/adaptive-demo",
    response_class=HTMLResponse,
)
def adaptive_demo() -> HTMLResponse:
    return HTMLResponse(
        HTML_FILE.read_text(
            encoding="utf-8"
        )
    )
