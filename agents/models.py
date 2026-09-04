"""
Pydantic v2 schemas and data definitions for Frozen Section Sentinel Agent.
Domain: Digital Pathology & Histology Systems
Standard: CAP Cancer Protocols / DICOM WSI PS3.16
"""
import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


MAX_ID_LENGTH = 128
MAX_STATUS_LENGTH = 64
MAX_METRIC_VALUE = 1e9


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., max_length=MAX_ID_LENGTH, description="Unique task / case identifier")
    target_identifier: str = Field(..., max_length=MAX_ID_LENGTH, description="Entity, patient key, or genomic/cryptographic target")
    primary_metric: float = Field(..., ge=-MAX_METRIC_VALUE, le=MAX_METRIC_VALUE, description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, ge=-MAX_METRIC_VALUE, le=MAX_METRIC_VALUE, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", max_length=MAX_STATUS_LENGTH, description="Status code or phenotype descriptor")
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id", "target_identifier")
    @classmethod
    def _sanitize_identifier(cls, v: str) -> str:
        # Strip control characters and leading/trailing whitespace
        sanitized = "".join(ch for ch in v if ch.isprintable())
        sanitized = sanitized.strip()
        if not sanitized:
            raise ValueError("Identifier cannot be empty or whitespace-only")
        return sanitized

    @field_validator("status_descriptor")
    @classmethod
    def _sanitize_status(cls, v: str) -> str:
        sanitized = "".join(ch for ch in v if ch.isprintable())
        return sanitized.strip()


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "CAP Cancer Protocols / DICOM WSI PS3.16"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "frozen-section-sentinel-agent"
    domain: str = "Digital Pathology & Histology Systems"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "CAP Cancer Protocols / DICOM WSI PS3.16"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
