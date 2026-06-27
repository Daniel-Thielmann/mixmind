# 🎧 MixMind

> **AI-powered DJ Track Analysis Platform**
>
> Analyze audio tracks, extract musical features and discover the best transitions between songs.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue)

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)

![License](https://img.shields.io/badge/license-MIT-blue)

![Tests](https://img.shields.io/badge/tests-pytest-success)

![Coverage](https://img.shields.io/badge/coverage-72%25-success)

![Status](https://img.shields.io/badge/status-In%20Development-orange)

</p>

---

# Overview

MixMind is an audio analysis platform designed to assist DJs and music producers by automatically extracting relevant musical information from tracks.

Instead of manually analyzing songs, the platform performs Digital Signal Processing (DSP) techniques to compute musical features and estimate how compatible two tracks are for mixing.

This project is being developed as the practical project for the **DCC082 – Sistemas Multimídia** course at the **Federal University of Juiz de Fora (UFJF)**.

---

# Features

Current features include:

- Audio upload
- Audio analysis using Librosa
- BPM estimation
- RMS Energy calculation
- Duration extraction
- Compatibility Engine
- REST API with FastAPI
- Interactive Swagger documentation
- Automated tests
- Continuous Integration
- Code Quality Pipeline

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

                      ▼

               FastAPI REST API

                      │

                      ▼

              AnalysisService

          ┌───────────┴───────────┐

          ▼                       ▼

   StorageService         AudioAnalyzer

                                  │

                                  ▼

                           Librosa DSP

                                  │

                                  ▼

                     CompatibilityService

                                  │

                                  ▼

                           JSON Response
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

## Audio Processing

- Librosa
- NumPy
- SciPy
- SoundFile

## Testing

- pytest
- pytest-cov

## Quality

- Ruff
- Black
- Pre-commit

## CI/CD

- GitHub Actions

---

# Project Structure

```text
MixMind-AI/

├── backend/
│
├── app/
│   ├── api/
│   ├── audio/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   └── utils/
│
├── tests/
│
├── uploads/
├── processed/
├── temp/
│
├── requirements.txt
└── requirements-dev.txt

├── frontend/

├── docs/

├── README.md
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

Create virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the server

```bash
uvicorn app.main:app --reload
```

Swagger

```
http://localhost:8000/docs
```

---

# Running Tests

```bash
pytest
```

Coverage

```bash
pytest --cov
```

---

# Code Quality

Run Ruff

```bash
ruff check .
```

Format

```bash
black .
```

Run pre-commit

```bash
pre-commit run --all-files
```

---

# Roadmap

## Phase 1

- [x] Project structure
- [x] REST API
- [x] Audio upload
- [x] BPM extraction
- [x] RMS Energy
- [x] Compatibility Engine

## Phase 2

- [ ] Waveform generation
- [ ] Spectrogram generation
- [ ] Dashboard API
- [ ] Audio normalization (FFmpeg)

## Phase 3

- [ ] React/Next.js frontend
- [ ] Track comparison interface
- [ ] Visualization dashboard

## Phase 4

- [ ] AI Recommendation Engine
- [ ] Key Detection
- [ ] Camelot Wheel
- [ ] Transition Suggestions
- [ ] Mix Quality Score

---

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
