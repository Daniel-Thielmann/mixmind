# Architecture

The project follows Clean Architecture principles.

---

# Current Flow

```text
Client

↓

FastAPI Endpoint

↓

AnalysisService

↓

StorageService

↓

AudioAnalyzer

↓

CompatibilityService

↓

Response
```

---

# Future Flow

```text
Client

↓

FastAPI

↓

AnalysisService

↓

Storage

↓

FFmpeg

↓

AudioAnalyzer

↓

WaveformGenerator

↓

SpectrogramGenerator

↓

FeatureExtractor

↓

CompatibilityService

↓

RecommendationEngine

↓

Response
```

---

# Responsibilities

Endpoints

Receive requests.

Validate input.

Call services.

Return schemas.

Never contain business logic.

---

AnalysisService

Acts as orchestrator.

Coordinates the workflow.

Never performs DSP calculations.

---

StorageService

Responsible only for storing uploaded files.

---

AudioAnalyzer

Responsible only for Digital Signal Processing.

Extracts:

- BPM
- Energy
- Sample Rate
- Duration

---

CompatibilityService

Compares two AudioAnalysis objects.

Returns CompatibilityResult.

---

Future Services

WaveformGenerator

SpectrogramGenerator

RecommendationEngine

FFmpegService

FeatureExtractor

Each service must have a single responsibility.
