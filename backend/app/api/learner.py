from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(
    tags=["Learner Platform"],
)

HTML_FILE = (
    Path(__file__).resolve().parents[1]
    / "web"
    / "learner.html"
)


@router.get(
    "/learner",
    response_class=HTMLResponse,
)
def learner_platform() -> HTMLResponse:
    return HTMLResponse(
        HTML_FILE.read_text(
            encoding="utf-8"
        )
    )
