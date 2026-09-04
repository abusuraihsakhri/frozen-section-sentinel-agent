"""
Automated Pytest for frozen-section-sentinel-agent Enrichment Modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from enrichment import (
    OverviewEngine,
    Enrichment1FrozentopermanentDiscordanceTrackingWithSeverityScoringEngine,
    Enrichment2RealtimeIntraoperativeTatMonitoringDashboardEngine,
    Enrichment3MarginDistanceMeasurementWithPositiveMarginAlertEngine,
    Enrichment4SurgeonnotificationWebsocketPushEngine,
    FrozensectionsentinelagentEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = FrozensectionsentinelagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)


def test_enrichment_threshold_escalation():
    suite = FrozensectionsentinelagentEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0


def test_enrichment_suite_no_duplicate_keys():
    """Verify execute_all returns unique keys (no overwrites)."""
    suite = FrozensectionsentinelagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    # All 5 engines should produce distinct keys
    assert len(res) == 5
    expected_keys = {
        "OverviewEngine",
        "Enrichment1FrozentopermanentDiscordanceTrackingWithSeverityScoringEngine",
        "Enrichment2RealtimeIntraoperativeTatMonitoringDashboardEngine",
        "Enrichment3MarginDistanceMeasurementWithPositiveMarginAlertEngine",
        "Enrichment4SurgeonnotificationWebsocketPushEngine",
    }
    assert set(res.keys()) == expected_keys


def test_enrichment_suite_single_implementation_engine():
    """Verify suite has no redundant implementationengine attribute overwrites."""
    suite = FrozensectionsentinelagentEnrichmentSuite()
    # Should have 5 distinct engine attributes, not overwriting implementationengine
    assert hasattr(suite, "overviewengine")
    assert hasattr(suite, "enrichment1frozentop")
    assert hasattr(suite, "enrichment2realtimei")
    assert hasattr(suite, "enrichment3margindis")
    assert hasattr(suite, "enrichment4surgeonno")
    # Should NOT have a stale implementationengine attribute
    assert not hasattr(suite, "implementationengine")
