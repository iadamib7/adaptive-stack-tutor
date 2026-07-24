from fastapi import FastAPI

app = FastAPI(
    title="Adaptive STACK Tutor",
    description="An adaptive learning platform for STACK mathematics.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Adaptive STACK Tutor API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}