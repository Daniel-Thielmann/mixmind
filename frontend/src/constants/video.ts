import type { DemoMetadata } from "@/types/video";

export const DEMO_METADATA: DemoMetadata = {
  src: process.env.NEXT_PUBLIC_DEMO_VIDEO_URL ?? "/demo/transition.mp3",
  poster: "/demo/poster.jpg",
  thumbnail: "/demo/thumbnail.jpg",
  title: "Samba → Povoada (Remix) — AI Transition Analysis",
  duration: 164,
  tracks: {
    a: {
      name: "Samba",
      artist: "VXSION & Luch-E",
      color: "#44f3d0",
      bpm: 124,
      key: "A Minor",
      camelot: "8A",
    },
    b: {
      name: "Povoada (Remix)",
      artist: "Maz (BR), Antdot & Sued Nunes",
      color: "#8b5cf6",
      bpm: 126,
      key: "C Major",
      camelot: "8B",
    },
  },
  chapters: [
    { time: 0, label: "Track A", type: "track-a" },
    { time: 45, label: "EQ Blend", type: "blend" },
    { time: 78, label: "Bass Swap", type: "transition" },
    { time: 92, label: "Peak Harmony", type: "peak" },
    { time: 125, label: "Track B Dominant", type: "track-b" },
  ],
  insights: [
    {
      time: 0,
      duration: 4,
      type: "transition",
      title: "Transition Started",
      description: "AI analyzing harmonic compatibility between tracks",
      confidence: 94,
    },
    {
      time: 45,
      duration: 5,
      type: "eq-swap",
      title: "EQ Swap",
      description: "High-pass filtering Track A — low frequencies blending in from Track B",
      confidence: 91,
    },
    {
      time: 62,
      duration: 4,
      type: "bass-transfer",
      title: "Bass Transfer",
      description: "Bass line shifting from A Minor root to C Major progression",
      confidence: 88,
    },
    {
      time: 78,
      duration: 4,
      type: "phrase-match",
      title: "Phrase Match",
      description: "8-bar phrases aligned — perfect structural lock",
      confidence: 96,
    },
    {
      time: 83,
      duration: 5,
      type: "camelot-match",
      title: "Camelot Match",
      description: "8A → 8B (+1) — harmonic key compatibility confirmed",
      confidence: 94,
    },
    {
      time: 92,
      duration: 4,
      type: "energy-shift",
      title: "Energy Peak",
      description: "Energy rising from 0.78 → 0.85 — optimal blend moment",
      confidence: 92,
    },
    {
      time: 125,
      duration: 4,
      type: "confidence",
      title: "Transition Complete",
      description: "Track B dominant — seamless blend verified. Score: 94/100",
      confidence: 94,
    },
  ],
  markers: [
    { time: 0, label: "5:10:00", type: "start" },
    { time: 45, label: "EQ Blend In", type: "blend" },
    { time: 78, label: "Bass Transfer", type: "event" },
    { time: 83, label: "5:11:23", type: "peak" },
    { time: 92, label: "Peak Harmony", type: "peak" },
    { time: 125, label: "Track B Settled", type: "chapter" },
    { time: 164, label: "5:12:44", type: "end" },
  ],
  transitionZones: [
    { startTime: 45, endTime: 92, label: "EQ Blend — Bass Transfer — Peak Harmony", type: "blend" },
    { startTime: 92, endTime: 125, label: "Track B Settling", type: "phrase-match" },
  ],
  compatibility: {
    score: 94,
    harmonicMatch: true,
    camelotTransition: "8A → 8B (+1)",
    bpmDiff: 2,
    energyDiff: 0.07,
  },
};

export const PLAYBACK_RATES = [0.5, 0.75, 1, 1.25, 1.5, 2] as const;

export const VOLUME_STEPS = 0.05;
