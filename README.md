# MixMind AI

[![Python](https://img.shields.io/badge/Python-3.12-3776AB)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Build](https://img.shields.io/badge/Build-GitHub%20Actions-2088FF)](.github/workflows/backend.yml)
[![Ruff](https://img.shields.io/badge/Lint-Ruff-2C7A7B)](https://docs.astral.sh/ruff/)

MixMind AI is a FastAPI and Next.js project for analyzing electronic music tracks
and calculating compatibility scores for DJ transitions.

## Architecture

The backend follows a layered architecture:

HTTP Request -> API Endpoint -> Application Service -> Infrastructure Service ->
Audio Processing -> Domain Models -> JSON Response

Current backend flow:

Upload -> StorageService -> AudioAnalyzer -> CompatibilityService ->
UploadAnalysisResponse

## Technologies

- Python 3.12
- FastAPI
- Pydantic v2
- Librosa
- NumPy
- SciPy
- Black
- Ruff
- isort
- pytest
- pre-commit

## How to Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

## How to Test

```bash
cd backend
pytest
ruff check .
black .
isort .
```

## Roadmap

- v0.3: Audio Analysis stabilization
- v0.4: Recommendation Engine
- v0.5: Dashboard
- v0.6: Waveform visualization
- v0.7: Spectrogram visualization
- v0.8: FFmpeg integration

## Project Structure

```text
backend/
  app/
    api/
    audio/
    core/
    schemas/
    services/
    utils/
  tests/
frontend/
```
