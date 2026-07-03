"""Tests for MixScoringService — M3 (mix_difficulty), M4 (transition_length),
M6 (dj_score).
"""

from app.services.mix_scoring_service import MixScoringService

service = MixScoringService()


# -----------------------------------------------------------------------
# DJ Score (M6)
# -----------------------------------------------------------------------


class TestDJScore:
    def test_excellent_score(self):
        result = service.compute(
            compatibility_score=98, tempo_difference=1.0, energy_difference=0.01
        )
        assert result.dj_score == 98

    def test_very_good_score(self):
        result = service.compute(
            compatibility_score=85, tempo_difference=3.0, energy_difference=0.03
        )
        assert result.dj_score == 85

    def test_good_score(self):
        result = service.compute(
            compatibility_score=70, tempo_difference=4.0, energy_difference=0.08
        )
        assert result.dj_score == 70

    def test_fair_score(self):
        result = service.compute(
            compatibility_score=50, tempo_difference=6.0, energy_difference=0.15
        )
        assert result.dj_score == 50

    def test_poor_score(self):
        result = service.compute(
            compatibility_score=20, tempo_difference=15.0, energy_difference=0.5
        )
        assert result.dj_score == 30

    def test_score_bounds(self):
        result = service.compute(
            compatibility_score=0, tempo_difference=99.0, energy_difference=1.0
        )
        assert 0 <= result.dj_score <= 100


# -----------------------------------------------------------------------
# Mix Difficulty (M3)
# -----------------------------------------------------------------------


class TestMixDifficulty:
    def test_very_easy(self):
        r = service.compute(
            compatibility_score=90, tempo_difference=1.0, energy_difference=0.01
        )
        assert r.mix_difficulty == "Very Easy"

    def test_easy(self):
        r = service.compute(
            compatibility_score=70, tempo_difference=3.0, energy_difference=0.06
        )
        assert r.mix_difficulty == "Easy"

    def test_medium(self):
        r = service.compute(
            compatibility_score=50, tempo_difference=6.0, energy_difference=0.12
        )
        assert r.mix_difficulty == "Medium"

    def test_hard(self):
        r = service.compute(
            compatibility_score=30, tempo_difference=10.0, energy_difference=0.3
        )
        assert r.mix_difficulty == "Hard"

    def test_expert(self):
        r = service.compute(
            compatibility_score=10, tempo_difference=20.0, energy_difference=0.5
        )
        assert r.mix_difficulty == "Expert"


# -----------------------------------------------------------------------
# Transition Length (M4)
# -----------------------------------------------------------------------


class TestTransitionLength:
    def test_very_easy_gives_64_bars(self):
        r = service.compute(
            compatibility_score=90, tempo_difference=1.0, energy_difference=0.01
        )
        assert r.recommended_transition_length == "64 bars"

    def test_easy_gives_32_bars(self):
        r = service.compute(
            compatibility_score=70, tempo_difference=3.0, energy_difference=0.06
        )
        assert r.recommended_transition_length == "32 bars"

    def test_medium_gives_32_bars(self):
        r = service.compute(
            compatibility_score=50, tempo_difference=6.0, energy_difference=0.12
        )
        assert r.recommended_transition_length == "32 bars"

    def test_hard_gives_16_bars(self):
        r = service.compute(
            compatibility_score=30, tempo_difference=10.0, energy_difference=0.3
        )
        assert r.recommended_transition_length == "16 bars"

    def test_expert_gives_8_bars(self):
        r = service.compute(
            compatibility_score=10, tempo_difference=20.0, energy_difference=0.5
        )
        assert r.recommended_transition_length == "8 bars"


# -----------------------------------------------------------------------
# MixScore dataclass
# -----------------------------------------------------------------------


class TestMixScoreShape:
    def test_returns_all_fields(self):
        r = service.compute(
            compatibility_score=75, tempo_difference=4.0, energy_difference=0.05
        )
        assert hasattr(r, "dj_score")
        assert hasattr(r, "mix_difficulty")
        assert hasattr(r, "recommended_transition_length")

    def test_fields_are_correct_types(self):
        r = service.compute(
            compatibility_score=75, tempo_difference=4.0, energy_difference=0.05
        )
        assert isinstance(r.dj_score, int)
        assert isinstance(r.mix_difficulty, str)
        assert isinstance(r.recommended_transition_length, str)
