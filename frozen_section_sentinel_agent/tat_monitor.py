"""
Real-Time Intraoperative TAT Monitoring for Frozen Section Sentinel Agent.
Track time-to-answer for frozen section cases with SLA monitoring.
"""
import datetime
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TATRecord:
    """Turnaround time record for a frozen section case."""
    case_id: str
    event_type: str
    start_time: str
    end_time: Optional[str] = None
    elapsed_minutes: Optional[float] = None
    within_sla: Optional[bool] = None


class TATMonitor:
    """Monitor frozen section turnaround times with SLA tracking."""

    DEFAULT_SLA_MINUTES = 20

    def __init__(self, sla_minutes: float = DEFAULT_SLA_MINUTES):
        self.sla_minutes = sla_minutes
        self.active_timers: Dict[str, dict] = {}
        self.completed: Dict[str, TATRecord] = {}

    def start_timer(self, case_id: str, event_type: str = "frozen_section"):
        self.active_timers[case_id] = {
            "start": datetime.datetime.now(datetime.timezone.utc),
            "event_type": event_type,
        }

    def stop_timer(self, case_id: str) -> Optional[TATRecord]:
        timer = self.active_timers.pop(case_id, None)
        if not timer:
            return None

        end_time = datetime.datetime.now(datetime.timezone.utc)
        elapsed = (end_time - timer["start"]).total_seconds() / 60

        record = TATRecord(
            case_id=case_id,
            event_type=timer["event_type"],
            start_time=timer["start"].isoformat(),
            end_time=end_time.isoformat(),
            elapsed_minutes=round(elapsed, 1),
            within_sla=elapsed <= self.sla_minutes,
        )
        self.completed[case_id] = record
        return record

    def get_tat_distribution(self) -> dict:
        times = [r.elapsed_minutes for r in self.completed.values() if r.elapsed_minutes is not None]
        if not times:
            return {"mean": 0, "median": 0, "p90": 0, "exceeding_sla": 0, "total_cases": 0}

        times.sort()
        n = len(times)
        return {
            "mean": round(statistics.mean(times), 1),
            "median": round(statistics.median(times), 1),
            "p90": round(times[int(n * 0.9)] if n >= 10 else times[-1], 1),
            "min": round(times[0], 1),
            "max": round(times[-1], 1),
            "exceeding_sla": sum(1 for t in times if t > self.sla_minutes),
            "sla_compliance_rate": round(sum(1 for t in times if t <= self.sla_minutes) / n * 100, 1),
            "total_cases": n,
            "sla_threshold_min": self.sla_minutes,
        }

    def get_active_cases(self) -> List[dict]:
        now = datetime.datetime.now(datetime.timezone.utc)
        active = []
        for case_id, timer in self.active_timers.items():
            elapsed = (now - timer["start"]).total_seconds() / 60
            active.append({
                "case_id": case_id,
                "event_type": timer["event_type"],
                "elapsed_min": round(elapsed, 1),
                "at_risk": elapsed > self.sla_minutes * 0.75,
            })
        return active
