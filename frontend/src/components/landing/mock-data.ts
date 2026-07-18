export const MOCK_TRACK_A = {
  title: "Deep House Session",
  artist: "DJ Aurora",
  bpm: 124,
  key: "A Minor",
  camelot: "8A",
  energy: 0.78,
  duration: 185,
};

export const MOCK_TRACK_B = {
  title: "Melodic Techno Mix",
  artist: "Synthwave Kid",
  bpm: 126,
  key: "C Major",
  camelot: "8B",
  energy: 0.85,
  duration: 210,
};

export const MOCK_COMPATIBILITY = {
  score: 94,
  harmonicMatch: true,
  bpmMatch: true,
  energyMatch: true,
  camelotTransition: "8A → 8B (+1)",
  bpmDiff: 2,
  energyDiff: 0.07,
};

export const MOCK_FEATURES = [
  {
    title: "AI Analysis",
    description: "Deep neural networks extract BPM, key, energy, and structural features from your tracks with high precision.",
    icon: "Sparkles",
  },
  {
    title: "Harmonic Compatibility",
    description: "Camelot wheel integration with AI-powered harmonic mixing suggestions for seamless transitions.",
    icon: "Music",
  },
  {
    title: "Waveform Visualization",
    description: "High-resolution waveform display with zoom, scroll, and phase analysis for precise cue point placement.",
    icon: "Waves",
  },
  {
    title: "Spectrogram Analysis",
    description: "Frequency spectrum visualization revealing the tonal and textural composition of your tracks.",
    icon: "Activity",
  },
  {
    title: "Transition Strategy",
    description: "AI generates step-by-step transition plans with cue points, EQ adjustments, and filter sweeps.",
    icon: "Route",
  },
  {
    title: "DJ Execution Timeline",
    description: "Visual timeline showing loop points, effect automation, and volume curves for professional mixes.",
    icon: "Timer",
  },
];

export const MOCK_TECHNOLOGIES = [
  { name: "Python", category: "Backend", icon: "Code2" },
  { name: "FastAPI", category: "Backend", icon: "Zap" },
  { name: "PostgreSQL", category: "Backend", icon: "Database" },
  { name: "scikit-learn", category: "ML", icon: "Brain" },
  { name: "LLM", category: "ML", icon: "MessageSquare" },
  { name: "NumPy", category: "ML", icon: "Sigma" },
  { name: "Docker", category: "Infra", icon: "Container" },
  { name: "React", category: "Frontend", icon: "Globe" },
  { name: "Next.js", category: "Frontend", icon: "Globe" },
];

export const MOCK_ROADMAP = [
  {
    sprint: "Sprint 1",
    title: "Core Analysis Engine",
    items: ["Audio upload & processing", "BPM detection", "Key detection", "Energy analysis"],
    status: "completed",
  },
  {
    sprint: "Sprint 2",
    title: "AI Recommendations",
    items: ["LLM integration", "Transition strategies", "Compatibility scoring", "DJ execution plans"],
    status: "completed",
  },
  {
    sprint: "Sprint 3",
    title: "Data Science & Visualization",
    items: ["Feature extraction pipeline", "Embedding visualization", "Cluster analysis", "Confidence metrics"],
    status: "in-progress",
  },
  {
    sprint: "Sprint 4",
    title: "Production & Scale",
    items: ["Real-time analysis", "Batch processing", "API marketplace", "Mobile support"],
    status: "planned",
  },
];

export const MOCK_DATASCIENCE_CARDS = [
  { title: "BPM Distribution", description: "Tempo spread across analyzed tracks", icon: "BarChart3", gradient: "from-emerald-500/20 to-teal-500/10" },
  { title: "Feature Clusters", description: "t-SNE projection of audio features", icon: "ScatterChart", gradient: "from-blue-500/20 to-purple-500/10" },
  { title: "Embedding Space", description: "High-dimensional feature embedding visualization", icon: "Network", gradient: "from-violet-500/20 to-pink-500/10" },
  { title: "Harmonic Map", description: "Camelot wheel key distribution overlay", icon: "CircleDot", gradient: "from-amber-500/20 to-orange-500/10" },
  { title: "Similarity Matrix", description: "Pairwise track similarity heatmap", icon: "Grid3x3", gradient: "from-cyan-500/20 to-blue-500/10" },
  { title: "AI Confidence", description: "Prediction confidence per analyzed feature", icon: "Gauge", gradient: "from-green-500/20 to-emerald-500/10" },
  { title: "Feature Importance", description: "SHAP-based feature contribution analysis", icon: "TrendingUp", gradient: "from-rose-500/20 to-red-500/10" },
  { title: "Correlation Heatmap", description: "Feature correlation matrix visualization", icon: "Table2", gradient: "from-indigo-500/20 to-violet-500/10" },
];

export const HOW_IT_WORKS = [
  { step: 1, title: "Upload Your Tracks", description: "Drag & drop or select two audio files. MixMind accepts MP3, WAV, FLAC, and AIFF formats up to 20MB each.", icon: "Upload" },
  { step: 2, title: "AI Analysis", description: "Deep learning models extract BPM, harmonic key, energy profile, and structural features from both tracks.", icon: "Cpu" },
  { step: 3, title: "Machine Learning", description: "Proprietary algorithms compute compatibility scores, detect optimal transition points, and evaluate mix difficulty.", icon: "Brain" },
  { step: 4, title: "Harmonic Recommendation", description: "Camelot wheel integration suggests harmonically compatible matches with energy-aware transition strategies.", icon: "Music4" },
  { step: 5, title: "Perfect Mix", description: "Receive a complete DJ execution timeline with cue points, EQ settings, filter sweeps, and volume automation.", icon: "Sparkles" },
];