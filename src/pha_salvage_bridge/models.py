"""
4D Time-Locked Multimodal Wearable + Outpatient EHR State Models (`models.py`).

Implements Direction A1: Enforces `t_avail <= t_landmark` across asynchronous
consumer wearable streams (`t_sync`) and outpatient EHR laboratory/imaging records
(`storetime` / `t_portal_release`), preventing two-timestamp lookahead leakage
and encoding unordered outpatient workup explicitly as `MISSING_UNORDERED`
(`Unavailable != Negative`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional


class EpistemicStatus(str, Enum):
    AVAILABLE_VERIFIED = "AVAILABLE_VERIFIED"
    PENDING_AT_LANDMARK = "PENDING_AT_LANDMARK"
    MISSING_UNORDERED = "MISSING_UNORDERED"
    FLAGGED_ARTIFACT = "FLAGGED_ARTIFACT"


@dataclass(frozen=True)
class WearableStreamSample:
    """Daily or continuous consumer wearable + smart-boot telemetry sample."""

    day_index: int
    t_event_hours: float  # Physiological measurement timestamp (e.g., hours post-discharge)
    t_sync_hours: float   # Cloud/phone sync availability timestamp
    rhr_bpm: float
    hrv_rmssd_ms: float
    sleep_hours: float
    step_count: int
    plantar_temp_asymmetry_c: float  # Smart offloading boot / foot mat delta T (deg C)
    boot_offloading_adherence_pct: float  # % of weight-bearing steps inside offloading boot
    body_weight_kg: float
    wearable_contact_quality: float = 0.98


@dataclass(frozen=True)
class OutpatientEHRRecord:
    """Outpatient laboratory, microbiology, or imaging record with two timestamps."""

    record_id: str
    feature_key: str
    label: str
    value: Optional[float]
    text_summary: str
    unit: str
    t_chart_hours: float  # Specimen draw / exam time (`charttime`)
    t_store_hours: float  # EHR verification / patient portal release time (`storetime`)
    is_two_stage_culture: bool = False


@dataclass
class TimeLockedPHALandmarkState:
    """
    Immutable-style 4D Time-Locked Multimodal State at `t_landmark_hours` post-discharge.
    """

    episode_id: str
    patient_id: str
    cohort_domain: str  # "POST_DFI_SALVAGE" or "POST_SEPSIS_CARDIORENAL"
    t_landmark_hours: float
    strict_storetime_lock: bool
    admitted_wearable_history: List[WearableStreamSample]
    admitted_ehr_records: Dict[str, OutpatientEHRRecord]
    pending_ehr_records: List[OutpatientEHRRecord]
    leaked_future_ehr_records_blocked: List[OutpatientEHRRecord]
    epistemic_map: Dict[str, EpistemicStatus]
    missing_indicators: Dict[str, int]
    merkle_root: str = ""

    def compute_merkle_root(self) -> str:
        payload = {
            "episode_id": self.episode_id,
            "patient_id": self.patient_id,
            "cohort_domain": self.cohort_domain,
            "t_landmark_hours": round(self.t_landmark_hours, 4),
            "strict_storetime_lock": self.strict_storetime_lock,
            "wearable_days": [w.day_index for w in self.admitted_wearable_history],
            "admitted_ehr": {
                k: {
                    "val": r.value,
                    "t_chart": round(r.t_chart_hours, 3),
                    "t_store": round(r.t_store_hours, 3),
                }
                for k, r in sorted(self.admitted_ehr_records.items())
            },
            "pending_ids": sorted(r.record_id for r in self.pending_ehr_records),
            "missing_indicators": dict(sorted(self.missing_indicators.items())),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


REQUIRED_OUTPATIENT_FEATURES: Dict[str, str] = {
    "serum_creatinine_mg_dl": "Outpatient Serum Creatinine (BMP)",
    "spot_urine_sodium_mmol_l": "Spot Urine Sodium (Natriuresis Check)",
    "nt_probnp_pg_ml": "NT-proBNP (Cardiac Wall Stress)",
    "crp_mg_l": "C-Reactive Protein (Inflammatory Trend)",
    "hba1c_pct": "Glycated Hemoglobin (HbA1c)",
    "wound_probe_or_culture": "Outpatient Deep Wound / Blood Culture Speciation",
    "pedal_doppler_toe_pressure_mmhg": "Outpatient Hallux Toe Pressure / Perfusion Check",
    "venous_pocus_vexus_grade": "Outpatient / Home Point-of-Care VExUS Congestion Grade",
}


def build_time_locked_pha_state(
    episode_id: str,
    patient_id: str,
    cohort_domain: str,
    t_landmark_hours: float,
    wearable_stream: List[WearableStreamSample],
    ehr_records: List[OutpatientEHRRecord],
    strict_storetime_lock: bool = True,
) -> TimeLockedPHALandmarkState:
    """
    Constructs a 4D Time-Locked Multimodal State for the Personal Health Agent.

    - When `strict_storetime_lock=True`, admits only wearable samples with `t_sync_hours <= t_landmark_hours`
      and EHR records with `t_store_hours <= t_landmark_hours`. Records drawn before `t_landmark_hours`
      (`t_chart_hours <= t_landmark_hours < t_store_hours`) are masked as `PENDING_AT_LANDMARK` and
      recorded in `leaked_future_ehr_records_blocked`.
    - When `strict_storetime_lock=False` (naive `charttime` baseline), any EHR record with
      `t_chart_hours <= t_landmark_hours` is admitted regardless of `t_store_hours`, exposing
      lookahead leakage.
    """
    admitted_wearables = [
        w for w in wearable_stream
        if (w.t_sync_hours if strict_storetime_lock else w.t_event_hours) <= t_landmark_hours
    ]
    admitted_wearables.sort(key=lambda x: x.t_event_hours)

    admitted_ehr: Dict[str, OutpatientEHRRecord] = {}
    pending_ehr: List[OutpatientEHRRecord] = []
    blocked_future: List[OutpatientEHRRecord] = []

    for rec in sorted(ehr_records, key=lambda r: r.t_chart_hours):
        if strict_storetime_lock:
            if rec.t_store_hours <= t_landmark_hours:
                admitted_ehr[rec.feature_key] = rec
            elif rec.t_chart_hours <= t_landmark_hours < rec.t_store_hours:
                pending_ehr.append(rec)
                blocked_future.append(rec)
            else:
                blocked_future.append(rec)
        else:
            if rec.t_chart_hours <= t_landmark_hours:
                admitted_ehr[rec.feature_key] = rec
            else:
                blocked_future.append(rec)

    epistemic_map: Dict[str, EpistemicStatus] = {}
    missing_indicators: Dict[str, int] = {}
    pending_keys = {r.feature_key for r in pending_ehr}

    for f_key in REQUIRED_OUTPATIENT_FEATURES:
        if f_key in admitted_ehr and admitted_ehr[f_key].value is not None:
            epistemic_map[f_key] = EpistemicStatus.AVAILABLE_VERIFIED
            missing_indicators[f"MISSING_IND__{f_key}"] = 0
        elif f_key in pending_keys:
            epistemic_map[f_key] = EpistemicStatus.PENDING_AT_LANDMARK
            missing_indicators[f"MISSING_IND__{f_key}"] = 1
        else:
            epistemic_map[f_key] = EpistemicStatus.MISSING_UNORDERED
            missing_indicators[f"MISSING_IND__{f_key}"] = 1

    state = TimeLockedPHALandmarkState(
        episode_id=episode_id,
        patient_id=patient_id,
        cohort_domain=cohort_domain,
        t_landmark_hours=t_landmark_hours,
        strict_storetime_lock=strict_storetime_lock,
        admitted_wearable_history=admitted_wearables,
        admitted_ehr_records=admitted_ehr,
        pending_ehr_records=pending_ehr,
        leaked_future_ehr_records_blocked=blocked_future,
        epistemic_map=epistemic_map,
        missing_indicators=missing_indicators,
    )
    state.merkle_root = state.compute_merkle_root()
    return state
