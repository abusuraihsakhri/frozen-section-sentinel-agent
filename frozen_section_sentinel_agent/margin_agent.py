"""
Margin Distance Measurement with Positive Margin Alert for Frozen Section Sentinel Agent.
Evaluate margin distances and classify per AJCC/CAP guidelines.
"""
from dataclasses import dataclass
import math
from typing import Dict, Optional


@dataclass
class MarginEvaluation:
    """Margin distance evaluation result."""
    distance_mm: float
    margin_type: str
    classification: str  # "Negative", "Close", "Positive"
    requires_reexcision: bool
    clinical_alert: bool
    recommended_margin_mm: float


class MarginMeasurementAgent:
    """Evaluate surgical margin distances with clinical alerting."""

    TUMOR_TYPE_MARGINS = {
        "melanoma": 1.0,
        "bcc": 2.0,
        "scc": 2.0,
        "breast": 2.0,
        "colon": 5.0,
        "oral_scc": 5.0,
        "thyroid": 1.0,
        "lung": 2.0,
        "prostate": 3.0,
    }

    def evaluate_margin_distance(self, distance_mm: float, margin_type: str) -> dict:
        if not math.isfinite(distance_mm) or distance_mm < 0:
            raise ValueError("Margin distance must be finite and non-negative")
        if distance_mm > 3:
            classification = "Negative"
        elif distance_mm > 0:
            classification = "Close"
        else:
            classification = "Positive"

        return {
            "distance_mm": distance_mm,
            "margin_type": margin_type,
            "classification": classification,
            "requires_reexcision": classification == "Positive",
            "clinical_alert": classification in ("Positive", "Close"),
            "alert_level": "CRITICAL" if classification == "Positive" else "WARNING" if classification == "Close" else "NONE",
        }

    def compute_safe_margin(self, lateral_mm: float, tumor_type: str) -> dict:
        if not math.isfinite(lateral_mm) or lateral_mm < 0:
            raise ValueError("Margin distance must be finite and non-negative")
        tumor_key = tumor_type.strip().lower()
        if tumor_key not in self.TUMOR_TYPE_MARGINS:
            raise ValueError("Unknown tumor type: an illustrative reference cannot be selected")
        required = self.TUMOR_TYPE_MARGINS[tumor_key]
        adequate = lateral_mm >= required
        return {
            "required_mm": required,
            "actual_mm": lateral_mm,
            "adequate": adequate,
            "tumor_type": tumor_type,
            "deficit_mm": round(max(0, required - lateral_mm), 1),
            "recommendation": "At or above the illustrative reference; verify the applicable clinical standard" if adequate else "Below the illustrative reference; refer to the site-specific pathology protocol",
        }

    def evaluate_all_margins(self, margins: Dict[str, float], tumor_type: str) -> dict:
        if not margins:
            raise ValueError("At least one margin measurement is required")
        results = {}
        positive_margins = []
        close_margins = []

        for margin_name, distance in margins.items():
            result = self.evaluate_margin_distance(distance, margin_name)
            results[margin_name] = result
            if result["classification"] == "Positive":
                positive_margins.append(margin_name)
            elif result["classification"] == "Close":
                close_margins.append(margin_name)

        overall = "Negative" if not positive_margins and not close_margins else "Positive" if positive_margins else "Close"

        return {
            "margins": results,
            "overall_status": overall,
            "positive_margins": positive_margins,
            "close_margins": close_margins,
            "requires_reexcision": len(positive_margins) > 0,
        }
