<div align="center">
  <br/>
  <img src="frontend/public/dash.png" alt="MixMind" width="800" style="border-radius: 8px;"/>
  <br/><br/>
  <h1>MixMind</h1>
  <p><strong>AI-powered DJ Mixing Assistant</strong></p>
  <p><strong>Professional audio analysis, transition planning and intelligent DJ recommendations.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.13-blue" alt="Python"/>
    <img src="https://img.shields.io/badge/FastAPI-Latest-green" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/Next.js-16-black" alt="Next.js"/>
    <img src="https://img.shields.io/badge/React-19-61DAFB" alt="React"/>
    <img src="https://img.shields.io/badge/Docker-Compose-2496ED" alt="Docker"/>
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="License"/>
    <img src="https://img.shields.io/badge/tests-158-success" alt="Tests"/>
    <img src="https://img.shields.io/badge/coverage-96%25-success" alt="Coverage"/>
    <img src="https://img.shields.io/badge/status-v1.0-success" alt="Status"/>
  </p>
  <br/>
</div>

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Data Pipeline & Machine Learning Models](#data-pipeline--machine-learning-models)
- [Scientific & Theoretical Context](#scientific--theoretical-context)
- [Contributing](#contributing)
- [License](#license)

---

## About

MixMind is an audio analysis platform designed to assist DJs and music producers by automatically extracting relevant musical information from tracks.

Instead of manually analyzing songs, the platform performs Digital Signal Processing (DSP) techniques to compute musical features and estimate how compatible two tracks are for mixing.

---

## Features

- AI-powered DJ track recommendations
- Professional DJ dashboard
- Audio upload and storage
- BPM estimation
- RMS Energy calculation
- Duration and sample rate extraction
- Waveform generation
- Spectrogram generation
- Compatibility Score
- MixMind Score
- AI Transition Guide
- Transition Timeline
- Radar Chart visualization
- Interactive waveform / spectrogram viewer
- REST API (FastAPI)
- Responsive Next.js frontend
- Docker support
- Automated tests with 96% coverage
- Continuous Integration (CI/CD)

---

## Tech Stack

| Category             | Technology                                                                            |
| -------------------- | ------------------------------------------------------------------------------------- |
| **Frontend**         | Next.js 16, React 19, TypeScript, Tailwind CSS, Framer Motion, Recharts, Lucide Icons |
| **Backend**          | Python 3.13, FastAPI, Pydantic / Pydantic Settings v2, Uvicorn, UV                    |
| **AI**               | OpenRouter, LLM Fallback Engine, Model Registry, Retry Strategy, Recommendation Cache |
| **Audio Processing** | Librosa, NumPy, SciPy, SoundFile                                                      |
| **Quality**          | Pytest / Pytest-cov, Ruff, MyPy (strict mode), Pre-commit hooks, GitHub Actions       |

---

## Architecture

The system follows a clean architecture pattern with a clear separation of concerns:

```text
                 User
                  |
         Next.js Dashboard
                  |
          FastAPI REST API
                  |
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
                  |
         Professional Dashboard
```

**Design decisions** are documented as Architecture Decision Records (ADRs) in [`docs/adr/`](docs/adr/), covering topics such as the use of UV, clean architecture, Pydantic Settings, logging, exception handling, domain model, aggregate design, repository pattern, and domain events.

---

## Project Structure

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
│   ├── tests/
│   ├── uploads/
│   ├── processed/
│   ├── temp/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── public/                 # Static assets (demo video, dash.png, etc.)
│   ├── Dockerfile
│   └── package.json
├── datasets/
├── ml/
├── llm/
├── pipelines/
├── notebooks/
├── infra/
├── monitoring/
├── docs/
│   ├── adr/                    # Architecture Decision Records
│   ├── architecture/
│   └── images/
├── scripts/
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## Prerequisites

- **Python 3.13+**
- **UV** (package manager) — install with `pip install uv`
- **Docker** and **Docker Compose** (optional, for containerized setup)
- **FFmpeg** (required for audio processing and demo asset generation)
- **yt-dlp** (required for demo asset generation)

---

## Installation & Setup

### Local Development

```bash
# Clone the repository
git clone https://github.com/Daniel-Thielmann/MixMind-AI.git

# Enter the backend directory
cd MixMind-AI/backend

# Install UV (package manager)
pip install uv

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Run the development server
uv run uvicorn app.main:app --reload

# Or use the pyproject script alias
uv run mixmind-run
```

The API will be available at `http://localhost:8000/docs` (Swagger UI).

### Docker

```bash
# Build and start all services
docker compose up --build

# Start a specific service (e.g., backend only)
docker compose up backend --build

# Stop all containers
docker compose down
```

| Service     | URL                          |
| ----------- | ---------------------------- |
| Backend API | `http://localhost:8000/docs` |
| Frontend    | `http://localhost:3000`      |

---

## Usage

### Running Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov
```

### Code Quality

```bash
# Lint with Ruff
uv run ruff check .

# Format with Ruff
uv run ruff format .

# Type check with MyPy (strict mode)
uv run mypy .

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Demo Assets

The landing page includes a demo video at `frontend/public/demo/clip_1080p.mp4`. This file (~48 MB) is **not versioned** — it is a generated artifact.

To regenerate all demo assets:

```bash
bash backend/scripts/extract-demo.sh \
  --url "https://youtu.be/GtSCkHk9fLw" \
  --start 18600 \
  --end 18764 \
  --output frontend/public/demo
```

The script downloads the full video, extracts a 164-second segment at 1920×1080, and generates poster / thumbnail images plus `metadata.json`.

---

## Data Pipeline & Machine Learning Models

### Audio Processing Pipeline

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

### Musical Features

**Current DSP features:**

- BPM estimation
- RMS Energy
- Duration
- Sample Rate

**Upcoming features:**

- Waveform Generation
- Spectrogram
- MFCC
- Chroma Features
- Harmonic / Percussive Separation
- Key Detection
- Camelot Wheel Compatibility

### v1.0 (Implemented)

- FastAPI backend with clean architecture
- Next.js professional dashboard
- Audio upload and storage pipeline
- BPM and RMS Energy extraction via Librosa
- Waveform and spectrogram generation
- Compatibility Engine scoring
- AI Recommendation Engine (OpenRouter LLM fallback)
- Docker support and automated tests (158 tests, 96% coverage)

### v2.0 Roadmap

| Track                    | Focus Areas                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------- |
| **Software Engineering** | FastAPI refinements, Docker orchestration, CI/CD, observability                       |
| **Data Engineering**     | Polars, Pandas, DuckDB, Parquet, Bronze / Silver / Gold layers, Airflow, Data Quality |
| **Machine Learning**     | Feature engineering, model evaluation, experiment tracking (MLflow), model serving    |
| **LLM Engineering**      | Embeddings, ChromaDB, RAG, LangChain, agents, prompt evaluation                       |
| **Platform Engineering** | Infrastructure as code, monitoring, deployment, scalability                           |

---

## Scientific & Theoretical Context

This project is being developed as the practical implementation of the course **DCC082 – Sistemas Multimídia** at the **Federal University of Juiz de Fora (UFJF)**.

The objective is to build production-quality software while demonstrating multimedia processing techniques grounded in:

- **Digital Signal Processing (DSP):** Feature extraction from audio signals using spectral analysis, Fourier transforms, and statistical descriptors.
- **Music Information Retrieval (MIR):** BPM estimation, key detection, harmonic mixing principles, and the Camelot Wheel system.
- **Recommendation Systems:** Compatibility scoring based on multi-dimensional feature vectors, weighted fusion of acoustic attributes, and LLM-augmented transition guidance.
- **Multimedia Systems Design:** Clean architecture, real-time processing pipelines, and responsive interfaces for professional audio workflows.

---

## License

This project is licensed under the MIT License.

---

<p align="center">
Developed by Daniel Thielmann
</p>
