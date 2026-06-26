from fastapi import FastAPI

app = FastAPI(
    title="MixMind AI API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"project": "MixMind AI", "status": "running"}
