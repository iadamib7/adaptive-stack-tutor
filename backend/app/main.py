from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.adaptive_sessions import (
    router as adaptive_sessions_router,
)
from backend.app.api.attempts import (
    router as attempts_router,
)
from backend.app.api.questions import (
    router as questions_router,
)
from backend.app.api.sessions import (
    router as sessions_router,
)
from backend.app.api.live_sessions import (
    router as live_sessions_router,
)
from backend.app.api.learner import (
    router as learner_router,
)
from backend.app.database.init_db import (
    initialize_database,
)
from backend.app.api.content import (
    router as content_router,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title="Adaptive STACK Tutor",
    description=(
        "A curriculum-independent adaptive mathematics "
        "assessment platform using instructor-authored "
        "STACK questions, learner-response evidence, "
        "and deterministic adaptive sequencing."
    ),
    version="0.4.0",
    lifespan=lifespan,
)

app.include_router(adaptive_sessions_router)
app.include_router(questions_router)
app.include_router(attempts_router)
app.include_router(sessions_router)
app.include_router(live_sessions_router)
app.include_router(learner_router)
app.include_router(content_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": (
            "Adaptive STACK Tutor API is running"
        )
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy"
    }
