"""Regression tests for integrity, CSV parsing, clinical screening guards and TAT."""
import csv
import math

import pytest

from agents.base import AuditTrail
from cli import main as root_main, parse_csv_bool as root_bool
from frozen_section_sentinel_agent.cli import main as package_main, parse_csv_bool as package_bool
from frozen_section_sentinel_agent.correlation import FrozenPermanentCorrelator
from frozen_section_sentinel_agent.margin_agent import MarginMeasurementAgent
from frozen_section_sentinel_agent.tat_monitor import TATMonitor, TATRecord


def test_hmac_verification_detects_mutation_and_detaches_public_copy():
    trail = AuditTrail("unit-test-key")
    trail.log("worker", "supervisor", "EVALUATED", {"status": "OK"})
    assert trail.verify_integrity()
    detached = trail.get_trail()
    detached[0]["actor"] = "attacker"
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "attacker"
    assert not trail.verify_integrity()


def test_hmac_verification_detects_replaced_hash_and_missing_field():
    trail = AuditTrail("unit-test-key")
    trail.log("worker", "supervisor", "A", {"foo": 1})
    trail.log("worker", "supervisor", "B", {"foo": 2})
    trail.logs[-1]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()
    trail.logs[-1].pop("actor")
    assert not trail.verify_integrity()


@pytest.mark.parametrize("parser", [root_bool, package_bool])
@pytest.mark.parametrize("value,expected", [("False", False), ("0", False), ("", False),
                                            ("no", False), ("TRUE", True), ("1", True)])
def test_csv_bool(parser, value, expected):
    assert parser(value) is expected


@pytest.mark.parametrize("parser", [root_bool, package_bool])
def test_csv_bool_rejects_ambiguous(parser):
    with pytest.raises(ValueError):
        parser("maybe")


@pytest.mark.parametrize("runner,header,record,status_column,expected", [
    (root_main, "task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag",
     "CASE-A,SYNTH-01,5,1,NOMINAL,False", "overall_urgency", "ROUTINE"),
    (package_main, "case_id,patient_synthetic_id,primary_metric,secondary_metric,status_flag,is_stat",
     "CASE-A,SYNTH-01,5,1,NORMAL,False", "overall_status", "CONCORDANT_NORMAL"),
])
def test_batch_false_flag_stays_false(tmp_path, runner, header, record, status_column, expected):
    inp = tmp_path / "cases.csv"
    out = tmp_path / "results.csv"
    inp.write_text(header + "\n" + record + "\n", encoding="utf-8")
    assert runner(["batch", "-i", str(inp), "-o", str(out)]) == 0
    with out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0][status_column] == expected


def test_different_malignant_diagnoses_require_review():
    engine = FrozenPermanentCorrelator()
    record = engine.correlate("SYNTH-01", "carcinoma", "melanoma")
    assert record.discordance_type == "Review"
    assert engine.get_discordance_rate() == 100.0
    assert engine.get_discordance_summary()["needs_review"] == 1
    assert engine.correlate("SYNTH-02", " carcinoma ", "CARCINOMA").discordance_type == "Concordant"


def test_tat_p90_nearest_rank_and_invalid_configuration():
    with pytest.raises(ValueError):
        TATMonitor(0)
    monitor = TATMonitor(20)
    for i in range(1, 11):
        monitor.completed[str(i)] = TATRecord(
            case_id=str(i), event_type="frozen_section", start_time="demo",
            elapsed_minutes=float(i), within_sla=True
        )
    assert monitor.get_tat_distribution()["p90"] == 9.0
    monitor.start_timer("SYNTH-01")
    with pytest.raises(ValueError):
        monitor.start_timer("SYNTH-01")


def test_margin_rejects_bad_measurements_and_unknown_types():
    m = MarginMeasurementAgent()
    with pytest.raises(ValueError):
        m.evaluate_margin_distance(math.nan, "medial")
    with pytest.raises(ValueError):
        m.evaluate_margin_distance(-2, "medial")
    with pytest.raises(ValueError):
        m.evaluate_all_margins({}, "melanoma")
    with pytest.raises(ValueError):
        m.compute_safe_margin(2.0, "unsupported_tumor")
