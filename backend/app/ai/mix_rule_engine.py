# ruff: noqa: E501
"""Rule engine — generates all technical recommendation fields deterministically."""

from __future__ import annotations

from typing import Any

from app.schemas.api import UploadAnalysisResponse
from app.services.mix_scoring_service import MixScore


class MixRuleEngine:
    """Produces deterministic technical analysis from backend metrics.

    Every method is a pure function of the input data.
    No LLM, no prompt, no randomness.
    """

    def build(
        self, response: UploadAnalysisResponse, mix_score: MixScore
    ) -> dict[str, Any]:
        return {
            "tempo_analysis": self._tempo_analysis(response),
            "energy_analysis": self._energy_analysis(response),
            "compatibility_analysis": self._compatibility_analysis(response),
            "transition_type": self._transition_type(response),
            "transition_quality": self._transition_quality(response),
            "mix_strategy": self._mix_strategy(response, mix_score),
            "dj_execution": self._dj_execution(response, mix_score),
            "risk_level": self._risk_level(mix_score),
            "risks": self._risks(response, mix_score),
            "best_use_case": self._best_use_case(response),
            "alternative_strategy": self._alternative_strategy(response),
            "why_this_strategy": self._why_this_strategy(response, mix_score),
            "transition_timeline": self._transition_timeline(mix_score),
        }

    @staticmethod
    def _tempo_analysis(response: UploadAnalysisResponse) -> dict[str, str]:
        diff = response.compatibility.tempo_difference
        bpm_a = response.track_a.bpm
        bpm_b = response.track_b.bpm

        if diff <= 0.5:
            difference = f"Only {diff:.1f} BPM apart — excellent tempo alignment."
            recommendation = "Use key lock and blend directly with no tempo adjustment."
        elif diff <= 2.0:
            difference = f"{diff:.1f} BPM difference — very close tempo alignment."
            recommendation = (
                "Apply a subtle pitch adjustment over 16 bars using key lock."
            )
        elif diff <= 5.0:
            difference = f"{diff:.1f} BPM difference — manageable tempo gap."
            recommendation = (
                f"Adjust Track B from {bpm_b:.0f} to {bpm_a:.0f} BPM "
                f"gradually over 32 bars."
            )
        elif diff <= 8.0:
            difference = f"{diff:.1f} BPM difference — noticeable tempo gap."
            recommendation = (
                "Use a loop bridge to transition. Adjust tempo during the loop."
            )
        else:
            difference = f"{diff:.1f} BPM difference — significant tempo gap."
            recommendation = (
                "Use a quick cut or echo out. Extended blends are not recommended."
            )

        return {"difference": difference, "recommendation": recommendation}

    @staticmethod
    def _energy_analysis(response: UploadAnalysisResponse) -> dict[str, str]:
        diff = response.compatibility.energy_difference
        energy_a = response.track_a.energy
        energy_b = response.track_b.energy

        if diff <= 0.02:
            difference = (
                "Energy delta is negligible — both tracks sit at the same intensity."
            )
            recommendation = (
                "Bring Track B in with full EQ and maintain the current energy curve."
            )
        elif diff <= 0.05:
            difference = f"Energy delta of {diff:.3f} — subtle energy shift."
            recommendation = (
                "Gradually introduce Track B with a slight high-pass filter on Track A."
            )
        elif diff <= 0.10:
            difference = f"Energy delta of {diff:.3f} — moderate energy shift."
            recommendation = (
                f"Track A is at {energy_a:.2f} and Track B at {energy_b:.2f}. "
                f"Reduce lows on Track A over 8 bars to ease the transition."
            )
        else:
            diff_dir = "higher" if energy_b > energy_a else "lower"
            difference = f"Energy delta of {diff:.3f} — significant energy difference."
            recommendation = (
                f"Track B is {diff_dir} energy. "
                f"Use EQ and filtering to smooth the shift over 16 bars."
            )

        return {"difference": difference, "recommendation": recommendation}

    @staticmethod
    def _compatibility_analysis(response: UploadAnalysisResponse) -> dict[str, str]:
        score = response.compatibility.compatibility_score
        rating = response.compatibility.overall_rating

        interpretation_map = {
            "Excellent": "The backend rates this pair as Excellent. The score supports a confident transition.",
            "Good": "The backend rates this pair as Good. Minor adjustments will yield a solid mix.",
            "Fair": "The backend rates this pair as Fair. Careful EQ and phrasing will be important.",
            "Poor": "The backend rates this pair as Poor. Significant manual intervention is required.",
        }
        interpretation = interpretation_map.get(rating, f"Backend rating: {rating}.")

        return {
            "score": f"{score:.0f}/100 — {rating} technical match.",
            "interpretation": interpretation,
        }

    @staticmethod
    def _transition_type(response: UploadAnalysisResponse) -> str:
        diff = response.compatibility.tempo_difference
        if diff <= 1.0:
            return "Long harmonic blend"
        if diff <= 3.0:
            return "Standard blend"
        if diff <= 6.0:
            return "Loop bridge"
        if diff <= 10.0:
            return "Quick cut"
        return "Echo out"

    @staticmethod
    def _transition_quality(response: UploadAnalysisResponse) -> str:
        score = response.compatibility.compatibility_score
        if score >= 85:
            return "High"
        if score >= 65:
            return "Medium"
        return "Low"

    @staticmethod
    def _mix_strategy(
        response: UploadAnalysisResponse, mix_score: MixScore
    ) -> dict[str, str]:
        tt = MixRuleEngine._transition_type(response)
        bars = mix_score.recommended_transition_length
        bars_num = int(bars.split()[0])

        if tt == "Long harmonic blend":
            before = f"Set a 4-beat cue point on Track B at bar 1. Align phrasing for a {bars} blend."
            during = (
                f"Start Track B on the one-count. Open highs over {bars_num // 2} bars."
            )
            after = f"Complete the blend by bar {bars_num}. Release any loops."
        elif tt == "Standard blend":
            before = f"Load Track B and cue the first beat. Prepare a {bars} blend."
            during = "Introduce Track B with mids only. Swap bass lines at the phrase change."
            after = f"Track A should be fully out by bar {bars_num}. Monitor levels."
        elif tt == "Loop bridge":
            before = (
                f"Set a {bars_num // 2}-bar loop on Track B's intro. Match the phase."
            )
            during = "Bring the loop in over 4 bars. Gradually open highs while reducing Track A's lows."
            after = "Release the loop at the next phrase. Track B takes over."
        elif tt == "Quick cut":
            before = "Prepare Track B at the cue point. Set a short loop on the outgoing track."
            during = "Cut Track A on the one-count and bring Track B in at full volume."
            after = "Immediately adjust gain if needed. Monitor the downbeat alignment."
        else:
            before = "Prepare an echo out on Track A's last phrase. Load Track B."
            during = "Trigger the echo effect and fade Track A. Start Track B on the next bar."
            after = "Verify BPM alignment and adjust pitch if necessary."

        return {
            "before_transition": before,
            "during_transition": during,
            "after_transition": after,
        }

    @staticmethod
    def _dj_execution(
        response: UploadAnalysisResponse, mix_score: MixScore
    ) -> dict[str, str]:
        tt = MixRuleEngine._transition_type(response)
        diff = response.compatibility.tempo_difference
        bars = mix_score.recommended_transition_length

        if diff <= 1.0:
            tempo_fader = "No adjustment needed — BPMs are nearly identical."
        elif diff <= 3.0:
            tempo_fader = f"Adjust pitch by {diff:.1f}% over {bars}."
        elif diff <= 6.0:
            tempo_fader = f"Use master tempo to adjust by {diff:.1f}%. Apply gradually."
        else:
            tempo_fader = (
                "Significant tempo difference. Adjust in headphones before bringing in."
            )

        if "blend" in tt.lower():
            loop = "4-bar loop on Track B entrance."
            eq = "Reduce lows on Track A over 8 bars. Open Track B with mids first."
            filter_sweep = (
                "Apply a high-pass filter on Track A sweeping from 40Hz to 250Hz."
            )
            phrase = "Match 16-bar phrases. Enter on bar 1 of a new phrase."
        elif "loop" in tt.lower():
            loop = "16-bar loop on Track B intro."
            eq = "Cut lows on Track A. Bring Track B in with full EQ."
            filter_sweep = "Open high-pass filter on Track A gradually over 8 bars."
            phrase = "Align loop start with the phrase boundary."
        elif "cut" in tt.lower():
            loop = "No loop needed — quick transition."
            eq = "Match EQs before the cut. No adjustment during transition."
            filter_sweep = "No filter needed."
            phrase = "Cut on the one-count. No phrase matching required."
        else:
            loop = "Set a 1-bar echo loop on Track A's last beat."
            eq = "Reduce lows on Track A. Bring Track B in at full EQ."
            filter_sweep = "Close the filter on Track A as Track B enters."
            phrase = "Start Track B immediately after the echo tail."

        return {
            "loop": loop,
            "eq": eq,
            "filter": filter_sweep,
            "tempo_fader": tempo_fader,
            "phrase_matching": phrase,
            "cue_point": "Set cue on the first beat of the target phrase.",
        }

    @staticmethod
    def _risk_level(mix_score: MixScore) -> str:
        mapping = {
            "Very Easy": "Low",
            "Easy": "Low",
            "Medium": "Medium",
            "Hard": "High",
            "Expert": "High",
        }
        return mapping.get(mix_score.mix_difficulty, "Medium")

    @staticmethod
    def _risks(response: UploadAnalysisResponse, mix_score: MixScore) -> list[str]:
        risks = []
        diff = response.compatibility.tempo_difference

        if diff > 5.0:
            risks.append(
                "Risk: Tempo drift|Impact: Beat alignment may degrade|"
                "Mitigation: Monitor pitch adjustment over the transition"
            )
        if response.compatibility.energy_difference > 0.08:
            risks.append(
                "Risk: Energy clash|Impact: Crowd energy may drop|"
                "Mitigation: Use EQ and filtering to smooth the shift"
            )
        if mix_score.mix_difficulty in ("Hard", "Expert"):
            risks.append(
                "Risk: Transition complexity|Impact: Execution error possible|"
                "Mitigation: Practice the transition before performing"
            )

        if not risks:
            risks.append(
                "Risk: None identified|Impact: Low|"
                "Mitigation: Standard monitoring during the transition"
            )

        return risks[:2]

    @staticmethod
    def _best_use_case(response: UploadAnalysisResponse) -> str:
        score = response.compatibility.compatibility_score
        if score >= 85:
            return "Peak-time or warm-up"
        if score >= 65:
            return "Mid-set programming"
        if score >= 40:
            return "Specialty or experimental"
        return "Practice or private use"

    @staticmethod
    def _alternative_strategy(response: UploadAnalysisResponse) -> str:
        tt = MixRuleEngine._transition_type(response)
        alt_map = {
            "Long harmonic blend": "Try a loop bridge if the blend feels too long.",
            "Standard blend": "Consider a quick cut for a more dramatic energy shift.",
            "Loop bridge": "Use a standard blend if phrasing alignment is clean.",
            "Quick cut": "Try a loop bridge for a smoother transition.",
            "Echo out": "Consider a quick cut for a more direct transition.",
        }
        return alt_map.get(tt, "")

    @staticmethod
    def _why_this_strategy(
        response: UploadAnalysisResponse, mix_score: MixScore
    ) -> str:
        diff = response.compatibility.tempo_difference
        score = response.compatibility.compatibility_score
        difficulty = mix_score.mix_difficulty

        if difficulty in ("Very Easy", "Easy"):
            return (
                f"BPM difference of {diff:.1f} and compatibility of {score:.0f}/100 "
                f"make this a straightforward blend requiring minimal intervention."
            )
        return (
            f"Strategy chosen based on tempo gap ({diff:.1f} BPM) "
            f"and compatibility score ({score:.0f}/100)."
        )

    @staticmethod
    def _transition_timeline(mix_score: MixScore) -> dict[str, str]:
        bars = mix_score.recommended_transition_length
        bars_num = int(bars.split()[0])

        if bars_num >= 64:
            return {
                "bar_1": "Start Track B intro",
                "bar_17": "Begin opening highs",
                "bar_33": "Swap bass lines",
                "bar_49": "Track A begins fade out",
                "bar_57": "Close filter on Track A",
                "bar_64": "Track B fully active",
            }
        if bars_num >= 32:
            return {
                "bar_1": "Start Track B intro",
                "bar_9": "Open highs gradually",
                "bar_17": "Swap bass lines",
                "bar_25": "Fade out Track A",
                "bar_32": "Track B fully active",
            }
        if bars_num >= 16:
            return {
                "bar_1": "Start Track B intro",
                "bar_9": "Swap bass lines and open highs",
                "bar_16": "Track B fully active",
            }
        return {
            "bar_1": "Start Track B",
            "bar_8": "Complete transition",
        }


mix_rule_engine = MixRuleEngine()
