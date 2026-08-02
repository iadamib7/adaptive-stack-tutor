from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from backend.app.api.attempts import router as attempts_router
from backend.app.api.questions import router as questions_router
from backend.app.database.init_db import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title="Adaptive STACK Tutor",
    description=(
        "An adaptive mathematics learning platform using "
        "student modeling and learning analytics."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

app.include_router(questions_router)
app.include_router(attempts_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Adaptive STACK Tutor API is running"
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy"
    }