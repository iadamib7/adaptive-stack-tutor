from fastapi import FastAPI

from backend.app.api.questions import router as questions_router

app = FastAPI(
    title="Adaptive STACK Tutor",
    description=(
        "An adaptive mathematics learning platform using "
        "student modeling and learning analytics."
    ),
    version="0.2.0",
)

app.include_router(questions_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Adaptive STACK Tutor API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}