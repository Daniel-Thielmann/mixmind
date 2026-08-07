<div align="center">
  <br/>
  <img src="https://yknudnlwdwelbdjwtlgc.supabase.co/storage/v1/object/public/mixmind-readme/readme/mixmind.webp" alt="MixMind home and Spotify analyzer flow" width="800" style="border-radius: 8px;"/>
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
- [Spotify Integration](#spotify-integration)
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
- Focused dashboard with recent analyses and Spotify integration status
- Audio upload or direct track selection from Spotify
- Owned Spotify playlists, saved tracks and catalog search
- Secure Spotify OAuth flow with automatic token refresh
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
│   ├── public/                 # Static assets (demo video, images, etc.)
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

### Analyze tracks from Spotify

1. Open the Analyzer and choose **Spotify** as the audio source.
2. Connect your Spotify account when prompted.
3. Select tracks from playlists you own, your saved tracks, or Spotify search.
4. Assign Track A and Track B, then start the analysis.

The Analyzer is the single workspace for track selection and analysis. The Dashboard remains focused on recent activity, quick actions, and integration status. Followed playlists are intentionally hidden because Spotify only permits track browsing for playlists owned by the connected user.

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

## Spotify Integration

MixMind supports an end-to-end Spotify workflow inside the Analyzer. Users can connect their account, select two tracks and run the same compatibility, DSP and AI recommendation pipeline used for uploaded audio files.

### Selection Sources

| Source | Behavior |
| ------ | -------- |
| **Owned Playlists** | Loads playlists owned by the connected Spotify account and supports paginated track browsing |
| **Saved Tracks** | Loads tracks saved in the user's Spotify library |
| **Search** | Searches the Spotify catalog for a specific track without requiring playlist access |

Followed playlists are intentionally excluded from the selector because Spotify does not expose their tracks through the API for this workflow. This keeps the interface focused on sources that can be browsed and analyzed successfully.

### OAuth Connection Flow

```text
Analyzer
  ↓
Next.js BFF
  ↓
FastAPI Spotify integration
  ↓
Spotify authorization
  ↓
Signed callback state validation
  ↓
Persistent connection in PostgreSQL
  ↓
Return to the original Analyzer destination
```

The OAuth state is signed, single-use and stored with an expiration time. Redirect destinations are restricted to known internal routes, preventing arbitrary callback redirects while preserving the user's original destination.

Access tokens are refreshed automatically before expiration. If Spotify returns `401 Unauthorized`, the backend performs one synchronized refresh and retries the request once. A successful new authorization can also safely transfer an existing Spotify connection when the same Spotify account is used with a different MixMind login identity.

### Spotify Analysis Pipeline

```text
Track A + Track B Spotify IDs
  ↓
Spotify metadata and duration
  ↓
External audio acquisition
  ↓
Content type, size and payload validation
  ↓
FFmpeg normalization when required
  ↓
Audio duration validation
  ↓
DSP and compatibility analysis
  ↓
AI transition recommendation
  ↓
Temporary file cleanup
```

The Spotify Web API provides catalog metadata but not the audio file required by the DSP pipeline. MixMind therefore uses a separately configured audio provider, validates the returned payload and rejects HTML, JSON, empty, oversized or duration-incompatible downloads before analysis.

### Required Backend Configuration

```bash
# Spotify OAuth application
SPOTIFY_CLIENT_ID=[spotify-client-id]
SPOTIFY_CLIENT_SECRET=[spotify-client-secret]
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/v1/integrations/spotify/callback
SPOTIFY_SCOPES="user-read-private user-read-email playlist-read-private playlist-read-collaborative user-library-read"

# Frontend destination and trusted BFF authentication
FRONTEND_URL=http://127.0.0.1:3000
INTERNAL_AUTH_SECRET=[shared-secret]

# Audio acquisition provider
RAPIDAPI_KEY=[rapidapi-key]
RAPIDAPI_SPOTIFY_DOWNLOADER_HOST=spotify-downloader9.p.rapidapi.com
RAPIDAPI_SPOTIFY_DOWNLOADER_BASE_URL=https://spotify-downloader9.p.rapidapi.com
RAPIDAPI_DOWNLOAD_TIMEOUT=60
RAPIDAPI_DOWNLOAD_MAX_SIZE=200
RAPIDAPI_REQUEST_TIMEOUT=30
```

### Required Frontend Configuration

```bash
# Browser and server-side backend destinations
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
BACKEND_API_URL=http://backend:8000

# Must match the backend value exactly
INTERNAL_AUTH_SECRET=[shared-secret]

# BFF timeout budgets
BACKEND_STATUS_TIMEOUT_MS=10000
BACKEND_SPOTIFY_TIMEOUT_MS=35000
BACKEND_ANALYSIS_TIMEOUT_MS=120000
```

For production, replace local addresses with the public frontend and backend HTTPS URLs. The exact value configured in `SPOTIFY_REDIRECT_URI` must also be registered as a Redirect URI in the Spotify Developer Dashboard.

| Environment | Spotify Redirect URI |
| ----------- | -------------------- |
| **Local** | `http://127.0.0.1:8000/api/v1/integrations/spotify/callback` |
| **Production** | `https://[backend-domain]/api/v1/integrations/spotify/callback` |

`INTERNAL_AUTH_SECRET` must contain the same strong value in the frontend and backend environments. Spotify credentials and RapidAPI keys are server-side secrets and must never be exposed through `NEXT_PUBLIC_*` variables or committed to the repository.

### Reliability and Error Handling

- Spotify library requests use explicit timeouts, pagination and request cancellation.
- Token refresh is synchronized per user to avoid duplicate concurrent refreshes.
- Owned playlists are filtered across all playlist pages before rendering.
- Provider URLs are downloaded with redirect support and CDN-compatible request headers.
- Temporary audio is removed after success or failure.
- Provider failures, invalid audio and duration mismatches return user-facing errors without exposing credentials or raw upstream responses.
- Reauthorization is requested when the refresh token is revoked, missing or no longer grants the required scopes.

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
