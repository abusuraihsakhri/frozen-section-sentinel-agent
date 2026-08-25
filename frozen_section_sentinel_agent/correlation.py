"""
Frozen-to-Permanent Discordance Tracking with Severity Scoring for Frozen Section Sentinel Agent.
Track and classify discrepancies between frozen and permanent section diagnoses.
"""
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DiscordanceRecord:
    """Record of frozen-permanent section discordance."""
    case_id: str
    frozen_dx: str
    permanent_dx: str
    discordance_type: str  # "Upgrade", "Downgrade", "Concordant"
    severity_score: float  # 0-10
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class FrozenPermanentCorrelator:
    """Track and classify frozen-permanent section discordances."""

    MALIGNANT_TERMS = [
        "cancer", "carcinoma", "malignant", "invasive", "adenocarcinoma",
        "melanoma", "sarcoma", "lymphoma", "neuroendocrine", "metastatic",
    ]

    def __init__(self):
        self.discordance_registry: List[DiscordanceRecord] = []

    def correlate(self, case_id: str, frozen_dx: str, permanent_dx: str) -> DiscordanceRecord:
        frozen_malignant = self._is_malignant(frozen_dx)
        permanent_malignant = self._is_malignant(permanent_dx)

        if not frozen_malignant and permanent_malignant:
            dtype, severity = "Upgrade", 8.0
        elif frozen_malignant and not permanent_malignant:
            dtype, severity = "Downgrade", 6.0
        else:
            dtype, severity = "Concordant", 0.0

        record = DiscordanceRecord(
            case_id=case_id,
            frozen_dx=frozen_dx,
            permanent_dx=permanent_dx,
            discordance_type=dtype,
            severity_score=severity,
        )
        self.discordance_registry.append(record)
        return record

    def get_discordance_rate(self) -> float:
        if not self.discordance_registry:
            return 0.0
        discordant = sum(1 for r in self.discordance_registry if r.discordance_type != "Concordant")
        return round(discordant / len(self.discordance_registry) * 100, 1)

    def get_discordance_summary(self) -> dict:
        total = len(self.discordance_registry)
        if total == 0:
            return {"total_cases": 0, "concordance_rate": 100.0}

        concordant = sum(1 for r in self.discordance_registry if r.discordance_type == "Concordant")
        upgrades = sum(1 for r in self.discordance_registry if r.discordance_type == "Upgrade")
        downgrades = sum(1 for r in self.discordance_registry if r.discordance_type == "Downgrade")

        return {
            "total_cases": total,
            "concordant": concordant,
            "upgrades": upgrades,
            "downgrades": downgrades,
            "concordance_rate": round(concordant / total * 100, 1),
            "upgrade_rate": round(upgrades / total * 100, 1),
            "downgrade_rate": round(downgrades / total * 100, 1),
            "mean_severity": round(sum(r.severity_score for r in self.discordance_registry) / total, 1),
        }

    def _is_malignant(self, dx: str) -> bool:
        dx_lower = dx.lower()
        return any(term in dx_lower for term in self.MALIGNANT_TERMS)
