```markdown
<div align="center">

# 🎧 MixMind AI

### AI-powered Assistant for Intelligent DJ Mixing

An intelligent multimedia platform capable of analyzing electronic music tracks and recommending harmonic and rhythmic transitions using Digital Signal Processing (DSP), Music Information Retrieval (MIR) and Artificial Intelligence.

---

**Federal University of Juiz de Fora (UFJF)**  
**DCC082 – Sistemas Multimídia**

**Academic Project – Trabalho Prático 2**

Developed by **Daniel Alves Thielmann**

</div>

---

## 📖 About the Project

MixMind AI is a web application designed to assist DJs in selecting compatible tracks and creating smoother transitions.

Instead of manually analyzing hundreds of songs, the user uploads two tracks and the system automatically extracts musical features such as:

- 🎵 BPM
- 🎼 Musical Key
- ⚡ Energy
- 🎧 Waveform
- 📊 Spectral Information
- 🥁 Beat Structure

Using these characteristics, the platform calculates a compatibility score and recommends the best transition point between the songs.

This project was proposed for the Multimedia Systems course and aims to integrate multiple concepts studied during the semester into a single multimedia application.

---

# 🎯 Objectives

The main objective is to demonstrate the integration of multimedia technologies in a practical application.

Specifically, the project aims to:

- Develop a modern Web application.
- Process digital audio files.
- Apply Music Information Retrieval techniques.
- Extract musical characteristics automatically.
- Recommend transitions between electronic music tracks.
- Demonstrate the use of Artificial Intelligence in multimedia.

---

# ✅ Requirements Covered

According to the course proposal, the application must satisfy at least two multimedia requirements.

MixMind AI satisfies four:

| Requirement | Status |
|------------|---------|
| Web Application | ✅ |
| Audio Processing | ✅ |
| Artificial Intelligence | ✅ |
| Audio Encoding / Transcoding | ✅ |

---

# 🧠 How It Works

The complete processing pipeline is illustrated below.

```

User Upload

```
    │

    ▼
```

FFmpeg Audio Conversion

```
    │

    ▼
```

Feature Extraction

• BPM
• Key
• Energy
• Spectrogram
• Beat Tracking

```
    │

    ▼
```

Recommendation Engine

```
    │

    ▼
```

Compatibility Score

```
    │

    ▼
```

Interactive Dashboard

```

---

# 🏗 System Architecture

```

```
            Frontend
    (Next.js + React)

           │

           ▼

    FastAPI Backend

           │

┌──────────┼──────────┐

▼          ▼          ▼
```

FFmpeg    Librosa    Essentia

```
│          │          │

└──────────┼──────────┘

           ▼

  Recommendation Engine

           ▼

  Analysis JSON Response

           ▼

  Interactive Dashboard
```

```

---

# 🚀 Main Features

### Upload audio tracks

Upload two music files.

---

### Automatic BPM Detection

Estimate the tempo of each track.

---

### Musical Key Detection

Estimate harmonic compatibility.

---

### Energy Estimation

Measure the perceived energy of each song.

---

### Compatibility Analysis

Generate an overall compatibility score.

---

### Mix Recommendation

Suggest the best transition point between songs.

---

### Audio Preview *(Future)*

Automatically generate a preview of the recommended mix.

---

# 🖥 Planned User Interface

```

---

```
           MixMind AI
```

---

Track A

Animals.mp3

128 BPM

11A

Energy 87

████████████

---

Track B

Spaceman.mp3

128 BPM

11B

Energy 91

█████████████

---

Compatibility

92%

⭐⭐⭐⭐☆

Recommended Mix

02:14

Crossfade

16 seconds

[ ▶ Preview ]

---

```

---

# 🛠 Technology Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

---

## Backend

- Python
- FastAPI

---

## Multimedia

- FFmpeg

---

## Audio Processing

- Librosa
- Essentia

---

## Machine Learning

- Scikit-learn
- NumPy
- SciPy

---

# 📂 Project Structure

```

MixMind-AI/

backend/

```
app/

    api/

    services/

    models/

    schemas/

    utils/
```

frontend/

```
app/

components/

hooks/

services/
```

docs/

assets/

README.md

```

---

# 📅 Development Roadmap

## Sprint 0

- [x] Project proposal
- [x] System architecture
- [x] Repository creation
- [ ] README
- [ ] Documentation

---

## Sprint 1

- [ ] FastAPI backend
- [ ] Next.js frontend
- [ ] Upload endpoint

---

## Sprint 2

- [ ] FFmpeg integration
- [ ] Audio conversion
- [ ] Waveform generation

---

## Sprint 3

- [ ] BPM extraction
- [ ] Musical Key detection
- [ ] Energy estimation

---

## Sprint 4

- [ ] Recommendation engine
- [ ] Dashboard

---

## Sprint 5

- [ ] Preview generation
- [ ] Final presentation

---

# 📚 Academic Context

This project is being developed as the final project for the course:

**DCC082 – Sistemas Multimídia**

Federal University of Juiz de Fora (UFJF)

Professor: Marcelo Moreno

---

# 📄 License

This project is licensed under the MIT License.
```
