# 🎧 MixMind

> **AI-powered DJ Mixing Assistant**
>
> Professional audio analysis, transition planning and intelligent DJ recommendations.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![React](https://img.shields.io/badge/React-19-61DAFB)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![License](https://img.shields.io/badge/license-MIT-blue)
![Tests](https://img.shields.io/badge/tests-158-success)
![Coverage](https://img.shields.io/badge/coverage-96%25-success)
![Status](https://img.shields.io/badge/status-v1.0-success)

</p>

---

# Overview

MixMind is an audio analysis platform designed to assist DJs and music producers by automatically extracting relevant musical information from tracks.

Instead of manually analyzing songs, the platform performs Digital Signal Processing (DSP) techniques to compute musical features and estimate how compatible two tracks are for mixing.

This project is being developed as the practical project for the **DCC082 – Sistemas Multimídia** course at the **Federal University of Juiz de Fora (UFJF)**.

---

# Screenshots

## Dashboard

![Dashboard](docs/images/dashboard.png)

## AI Recommendation

![AI Recommendation](docs/images/ai_recommendation.png)

## Track Analysis

![Track Analysis](docs/images/track.png)

---

# Features

- AI-powered DJ track recommendations
- Professional DJ dashboard
- Audio upload
- BPM estimation
- RMS Energy calculation
- Duration extraction
- Waveform generation
- Spectrogram generation
- Compatibility Score
- MixMind Score
- AI Transition Guide
- Transition Timeline
- Radar Chart visualization
- Interactive waveform/spectrogram viewer
- REST API (FastAPI)
- Responsive Next.js frontend
- Docker support
- Automated tests
- Continuous Integration

---

# Example Response

```json
{
  "track_a": {
    "filename": "Piece Of Your Heart.mp3",
    "duration": 152.91,
    "sample_rate": 44100,
    "bpm": 123.05,
    "energy": 0.2403
  },
  "track_b": {
    "filename": "Stolen Dance.mp3",
    "duration": 121.87,
    "sample_rate": 44100,
    "bpm": 129.2,
    "energy": 0.2639
  },
  "compatibility": {
    "compatibility_score": 60.1,
    "tempo_difference": 6.15,
    "energy_difference": 0.0236,
    "tempo_match": "Good",
    "energy_match": "Very Good",
    "overall_rating": "Good"
  }
}
```

---

# Architecture

```text
                                    User

                   │

         Next.js Dashboard

                   │

          FastAPI REST API

                   │

        Analysis Pipeline

      ┌──────────┴──────────┐

      ▼                     ▼

Audio Analyzer        AI Recommendation

      │                     │

      ▼                     ▼

 Librosa DSP         OpenRouter LLM

      │                     │

      └──────────┬──────────┘

                 ▼

         Compatibility Engine

                 ▼

         Professional Dashboard
```

---

# Tech Stack

## Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Framer Motion
- Recharts
- Lucide Icons

## Backend

- Python 3.13
- FastAPI
- Pydantic / Pydantic Settings v2
- Uvicorn
- UV (Python package manager)

## AI

- OpenRouter
- LLM Fallback Engine
- Model Registry
- Retry Strategy
- Recommendation Cache

## Audio Processing

- Librosa
- NumPy
- SciPy
- SoundFile

## Quality

- Pytest / Pytest-cov
- Ruff (linter + formatter)
- MyPy (strict mode)
- Pre-commit hooks
- GitHub Actions

---

# Project Structure

```text
MixMind-AI/

├── backend/
│   ├── app/
│   │   ├── api/               # Interface layer (FastAPI routers)
│   │   ├── application/        # Use cases / application services
│   │   ├── core/               # Config, logging, exceptions, security
│   │   ├── domain/             # Business entities, domain schemas
│   │   ├── infrastructure/     # External services (AI, audio, storage)
│   │   ├── shared/             # Shared utilities & helpers
│   │   └── main.py             # FastAPI application entry point
│   │
│   ├── tests/
│   ├── uploads/
│   ├── processed/
│   ├── temp/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── datasets/
├── ml/
├── llm/
├── pipelines/
├── notebooks/
├── infra/
├── monitoring/
├── docs/
├── scripts/
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── LICENSE
```

---

# Audio Processing Pipeline

```
Upload

↓

Storage

↓

Librosa

↓

Feature Extraction

↓

Compatibility Analysis

↓

REST Response
```

---

# Musical Features

Current DSP features:

- BPM estimation
- RMS Energy
- Duration
- Sample Rate

Upcoming features:

- Waveform Generation
- Spectrogram
- MFCC
- Chroma Features
- Harmonic/Percussive Separation
- Key Detection
- Camelot Wheel Compatibility

---

# Running Locally

Clone the repository

```bash
git clone https://github.com/Daniel-Thielmann/MixMind-AI.git
```

Enter the project

```bash
cd MixMind-AI/backend
```

Install UV (package manager)

```bash
pip install uv
```

Create virtual environment and install dependencies

```bash
cd backend
uv sync
```

Activate virtual environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Run the development server

```bash
uv run uvicorn app.main:app --reload
```

Or use the pyproject script

```bash
uv run mixmind-run
```

Swagger

```
http://localhost:8000/docs
```

---

# Running with Docker

Build and start all services

```bash
docker compose up --build
```

Run specific service

```bash
docker compose up backend --build
```

Backend

```
http://localhost:8000/docs
```

Frontend

```
http://localhost:3000
```

Stop containers

```bash
docker compose down
```

---

# Running Tests

```bash
uv run pytest
```

Coverage

```bash
uv run pytest --cov
```

---

# Code Quality

Run Ruff (linter)

```bash
uv run ruff check .
```

Run Ruff (formatter)

```bash
uv run ruff format .
```

Run MyPy (type checker)

```bash
uv run mypy .
```

Run pre-commit on all files

```bash
uv run pre-commit run --all-files
```

---

# Roadmap

## Version 1.0 ✅

- [x] FastAPI Backend
- [x] Next.js Frontend
- [x] Audio Upload
- [x] BPM Estimation
- [x] RMS Energy
- [x] Waveform Generation
- [x] Spectrogram Generation
- [x] Compatibility Engine
- [x] AI Recommendation Engine
- [x] Professional Dashboard
- [x] Docker Support
- [x] Automated Tests

## Future Versions

- [ ] Key Detection
- [ ] Camelot Wheel Analysis
- [ ] Harmonic Mixing
- [ ] Playlist Optimization
- [ ] Spotify Integration
- [ ] Rekordbox Export
- [ ] Real-time Audio Analysis

---

# New Roadmap for v2

🏗️ Trilha 1 — Software Engineering
Arquitetura
FastAPI
Docker
Testes
CI/CD
Observabilidade

📊 Trilha 2 — Data Engineering
Polars
Pandas
DuckDB
Parquet
Bronze/Silver/Gold
Airflow
Data Quality

🤖 Trilha 3 — Machine Learning
Feature Engineering
Modelagem
Avaliação
Experiment Tracking
MLflow
Model Serving

🧠 Trilha 4 — LLM Engineering
Embeddings
ChromaDB
RAG
LangChain
Agentes
Avaliação de prompts

☁️ Trilha 5 — Platform Engineering
Docker
Infraestrutura
Monitoramento
Deploy
Escalabilidade

# Academic Context

This project is being developed for the course:

**DCC082 – Sistemas Multimídia**

Federal University of Juiz de Fora (UFJF)

The goal is to demonstrate the integration of multimedia techniques, digital audio processing and modern software engineering practices.

---

# Contributing

Contributions are welcome.

Before contributing:

- Follow the coding standards.
- Run all tests.
- Execute pre-commit hooks.
- Open a Pull Request.

---

# License

This project is licensed under the MIT License.

---

<p align="center">

Developed by Daniel Alves Thielmann

</p>
