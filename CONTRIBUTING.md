# Contributing to MixMind AI

Thank you for improving MixMind AI.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Run

```bash
cd backend
uvicorn app.main:app --reload
```

## Test

```bash
cd backend
pytest
```

## Code Quality

```bash
ruff check .
black .
isort .
```

## Contribution Flow

1. Create a feature branch.
2. Make focused changes.
3. Run the quality checks.
4. Open a pull request with a concise summary.
