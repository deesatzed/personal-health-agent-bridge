"""
`pha_salvage_bridge`: Bidirectional Inpatient-to-Home Personal Health Agent (`PHA`)
and 4D Spatio-Temporal Clinical Router (`SALVAGE-AI`) Integration Package.

Combines the 3-specialist Personal Health Agent architecture (`DS` Data Science,
`DE` Domain Expert, `HC` Health Coach) with:
  1. Strict 4D Bitemporal Continuity (`t_event <= t_sync <= t_landmark` for wearables
     and `t_chart <= t_store <= t_landmark` for outpatient labs/cultures).
  2. Bidirectional Inpatient -> Home Discharge Handoff & Home -> Clinic VOI Escalation.
  3. Target-Trial Counterfactual Guardrails for Outpatient Prescription & Stewardship.
  4. Apple Vision Pro (`visionOS 27.0` / `iPadOS 27.0`) Spatial Decision Crossroads &
     `M0–M5` Symbiosis Decision-Model Gate (`VisionProSpatialGate`).
"""

from pha_salvage_bridge.models import (
    WearableStreamSample,
    OutpatientEHRRecord,
    TimeLockedPHALandmarkState,
    build_time_locked_pha_state,
)
from pha_salvage_bridge.agents import (
    DataScienceSubAgent,
    DomainExpertSubAgent,
    HealthCoachSubAgent,
    PersonalHealthOrchestrator,
    PHAConsolidatedResponse,
)
from pha_salvage_bridge.vision_pro_spatial_gate import (
    VisionProSpatialGate,
    VisionProSpatialGateProfile,
)
from pha_salvage_bridge.benchmark import run_bidirectional_pha_benchmark

__all__ = [
    "WearableStreamSample",
    "OutpatientEHRRecord",
    "TimeLockedPHALandmarkState",
    "build_time_locked_pha_state",
    "DataScienceSubAgent",
    "DomainExpertSubAgent",
    "HealthCoachSubAgent",
    "PersonalHealthOrchestrator",
    "PHAConsolidatedResponse",
    "VisionProSpatialGate",
    "VisionProSpatialGateProfile",
    "run_bidirectional_pha_benchmark",
]
