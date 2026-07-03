from app.ai.agent import DJAgent
from app.ai.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)
from app.schemas.api import UploadAnalysisResponse
from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult
from app.schemas.spectrogram import SpectrogramResult, Spectrograms
from app.schemas.waveform import WaveformResult, Waveforms

agent = DJAgent()

response = UploadAnalysisResponse(
    status="success",
    message="Tracks analyzed successfully",
    analysis_id="test-integration",
    track_a=AudioAnalysis(
        filename="Piece Of Your Heart.mp3",
        bpm=123.05,
        energy=0.2403,
        duration=152.91,
        sample_rate=44100,
    ),
    track_b=AudioAnalysis(
        filename="Stolen Dance.mp3",
        bpm=129.20,
        energy=0.2639,
        duration=121.87,
        sample_rate=44100,
    ),
    compatibility=CompatibilityResult(
        compatibility_score=60.1,
        tempo_difference=6.15,
        energy_difference=0.0236,
        tempo_match="Good",
        energy_match="Good",
        overall_rating="Good",
    ),
    ai_recommendation=AIRecommendationResponse(
        summary="",
        mix_direction="",
        transition_quality="",
        transition_type="",
        confidence=0,
        tempo_analysis=TempoAnalysis(difference="", recommendation=""),
        energy_analysis=EnergyAnalysis(difference="", recommendation=""),
        compatibility_analysis=CompatibilityAnalysis(score="", interpretation=""),
        mix_strategy=MixStrategy(
            before_transition="",
            during_transition="",
            after_transition="",
        ),
        dj_execution=DJExecution(
            loop="",
            eq="",
            filter="",
            tempo_fader="",
            phrase_matching="",
            cue_point="",
        ),
        club_tip="",
        professional_notes="",
        risks=[],
        best_use_case="",
        risk_level="",
    ),
    waveforms=Waveforms(
        track_a=WaveformResult(image_path="", width=1200, height=300),
        track_b=WaveformResult(image_path="", width=1200, height=300),
    ),
    spectrograms=Spectrograms(
        track_a=SpectrogramResult(image_path="", width=1200, height=500),
        track_b=SpectrogramResult(image_path="", width=1200, height=500),
    ),
)

recommendation = agent.recommend(response)

print(recommendation)
