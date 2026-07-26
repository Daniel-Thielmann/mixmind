<div align="center">
  <br/>
  <img src="frontend\public\dash.png" alt="MixMind" width="800" style="border-radius: 8px;"/>
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
- [Audio Processing Pipeline](#audio-processing-pipeline)
- [Musical Features](#musical-features)
- [Demo Assets](#demo-assets)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Roadmap](#roadmap)
- [New Roadmap for v2](#new-roadmap-for-v2)
- [Academic Context](#academic-context)
- [Contributing](#contributing)
- [License](#license)

---

# About

MixMind is an audio analysis platform designed to assist DJs and music producers by automatically extracting relevant musical information from tracks.

Instead of manually analyzing songs, the platform performs Digital Signal Processing (DSP) techniques to compute musical features and estimate how compatible two tracks are for mixing.

This project is being developed as the practical project for the **DCC082 – Sistemas Multimídia** course at the **Federal University of Juiz de Fora (UFJF)**.

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

# Tech Stack

| Category | Technology |
|---|---|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS, Framer Motion, Recharts, Lucide Icons |
| **Backend** | Python 3.13, FastAPI, Pydantic / Pydantic Settings v2, Uvicorn, UV |
| **AI** | OpenRouter, LLM Fallback Engine, Model Registry, Retry Strategy, Recommendation Cache |
| **Audio Processing** | Librosa, NumPy, SciPy, SoundFile |
| **Quality** | Pytest / Pytest-cov, Ruff, MyPy (strict mode), Pre-commit hooks, GitHub Actions |

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

# Demo Assets

The landing page includes a demo video at `frontend/public/demo/clip_1080p.mp4`.

**This file is not versioned** (~48 MB). It is a generated artifact.

To regenerate all demo assets, run:

```bash
bash backend/scripts/extract-demo.sh \
  --url "https://youtu.be/GtSCkHk9fLw" \
  --start 18600 \
  --end 18764 \
  --output frontend/public/demo
```

Prerequisites:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)

The script downloads the full video, extracts a 164‑second segment at 1920×1080,
and generates poster/thumbnail images + `metadata.json`.

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

---

# License

This project is licensed under the MIT License.

---

<p align="center">

Developed by Daniel Alves Thielmann

</p>
