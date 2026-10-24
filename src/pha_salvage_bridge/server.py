"""
Standalone HTTP Server & Two-Tier Frontend (`/landing` + `/workspace`) for `PHA × SALVAGE-AI` Bridge (`server.py`).

Runs on port 8790 (`http://127.0.0.1:8790`) so it never conflicts with the
`spatial-clinical-router` server on port 8780.
  - `/landing` -> 3D Showpiece Landing Page (`static/landing.html`)
  - `/workspace` (and `/`) -> Live Interactive Clinical & Wearable Simulation Console (`static/workspace.html`)
  - `GET /api/benchmark` -> Full N=160 benchmark JSON
  - `GET /api/scenario/<id>` -> Single flagship scenario JSON
  - `POST /api/simulate` -> Real-time 4D state + Coral NPU + 3-Agent PHA simulation
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import sys
from typing import Any, Dict, List
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pha_salvage_bridge.agents import PersonalHealthOrchestrator
from pha_salvage_bridge.benchmark import run_bidirectional_pha_benchmark
from pha_salvage_bridge.models import (
    OutpatientEHRRecord,
    REQUIRED_OUTPATIENT_FEATURES,
    WearableStreamSample,
    build_time_locked_pha_state,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_LANDING_PATH = STATIC_DIR / "landing.html"
STATIC_WORKSPACE_PATH = STATIC_DIR / "workspace.html"


def simulate_custom_pha_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Constructs a live 4D TimeLockedPHALandmarkState from UI controls and runs the 3-agent orchestrator."""
    episode_id = str(payload.get("episode_id", "PHA-SIM-01"))
    cohort_domain = str(payload.get("cohort_domain", "POST_DFI_SALVAGE"))
    temp_c = float(payload.get("plantar_temp_asymmetry_c", 2.6))
    weight_delta = float(payload.get("weight_delta_kg", 0.3))
    rhr_bpm = float(payload.get("rhr_bpm", 88.0))
    hrv_ms = float(payload.get("hrv_rmssd_ms", 24.0))
    boot_pct = float(payload.get("boot_offloading_adherence_pct", 52.0))
    strict_lock = bool(payload.get("strict_storetime_lock", True))
    verified_keys: List[str] = list(payload.get("verified_outpatient_keys", []))

    t_landmark = 168.0
    base_weight = 82.0
    wearables = [
        WearableStreamSample(
            day_index=1,
            t_event_hours=24.0,
            t_sync_hours=24.2,
            rhr_bpm=71.0,
            hrv_rmssd_ms=42.0,
            sleep_hours=7.5,
            step_count=3100,
            plantar_temp_asymmetry_c=0.6,
            boot_offloading_adherence_pct=92.0,
            body_weight_kg=base_weight,
        ),
        WearableStreamSample(
            day_index=4,
            t_event_hours=96.0,
            t_sync_hours=96.2,
            rhr_bpm=round((71.0 + rhr_bpm) / 2.0, 1),
            hrv_rmssd_ms=round((42.0 + hrv_ms) / 2.0, 1),
            sleep_hours=7.0,
            step_count=3600,
            plantar_temp_asymmetry_c=round((0.6 + temp_c) / 2.0, 2),
            boot_offloading_adherence_pct=round((92.0 + boot_pct) / 2.0, 1),
            body_weight_kg=round(base_weight + weight_delta * 0.5, 2),
        ),
        WearableStreamSample(
            day_index=7,
            t_event_hours=167.0,
            t_sync_hours=167.2,
            rhr_bpm=rhr_bpm,
            hrv_rmssd_ms=hrv_ms,
            sleep_hours=6.4 if temp_c >= 2.0 or weight_delta >= 1.5 else 7.6,
            step_count=5100 if boot_pct < 65.0 else 3200,
            plantar_temp_asymmetry_c=temp_c,
            boot_offloading_adherence_pct=boot_pct,
            body_weight_kg=round(base_weight + weight_delta, 2),
        ),
    ]

    ehr_records: List[OutpatientEHRRecord] = []
    # Default delayed outpatient records (drawn at 164h charttime, posted at 176h-212h storetime)
    default_delayed = [
        ("crp_mg_l", 48.0 if temp_c >= 2.0 else 6.0, "mg/L", 164.0, 176.0, False),
        ("wound_probe_or_culture", 1.0 if temp_c >= 2.0 else 0.0, "binary", 164.0, 212.0, True),
        ("serum_creatinine_mg_dl", 2.35 if weight_delta >= 1.8 else 1.72, "mg/dL", 164.0, 178.0, False),
    ]
    for f_key, val, unit, t_chart, t_store, is_cult in default_delayed:
        eff_store = 165.0 if f_key in verified_keys else t_store
        ehr_records.append(
            OutpatientEHRRecord(
                record_id=f"SIM_{f_key}",
                feature_key=f_key,
                label=REQUIRED_OUTPATIENT_FEATURES[f_key],
                value=val,
                text_summary=f"Simulated {f_key}={val} {unit}",
                unit=unit,
                t_chart_hours=t_chart,
                t_store_hours=eff_store,
                is_two_stage_culture=is_cult,
            )
        )

    for v_key in verified_keys:
        if all(r.feature_key != v_key for r in ehr_records) and v_key in REQUIRED_OUTPATIENT_FEATURES:
            val_map = {
                "pedal_doppler_toe_pressure_mmhg": 52.0,
                "spot_urine_sodium_mmol_l": 84.0 if weight_delta < 0 else 18.0,
                "venous_pocus_vexus_grade": 1.0 if weight_delta < 0 else 3.0,
                "nt_probnp_pg_ml": 420.0,
                "hba1c_pct": 7.1,
            }
            ehr_records.append(
                OutpatientEHRRecord(
                    record_id=f"SIM_ORD_{v_key}",
                    feature_key=v_key,
                    label=REQUIRED_OUTPATIENT_FEATURES[v_key],
                    value=val_map.get(v_key, 1.0),
                    text_summary=f"Ordered & Verified {v_key}",
                    unit="verified",
                    t_chart_hours=165.0,
                    t_store_hours=166.0,
                )
            )

    state = build_time_locked_pha_state(
        episode_id=episode_id,
        patient_id="PHA_LIVE_SIM",
        cohort_domain=cohort_domain,
        t_landmark_hours=t_landmark,
        wearable_stream=wearables,
        ehr_records=ehr_records,
        strict_storetime_lock=strict_lock,
    )
    orch = PersonalHealthOrchestrator()
    resp = orch.run_episode_landmark(state)
    return asdict(resp)


class PHABridgeRequestHandler(BaseHTTPRequestHandler):
    benchmark_cache = None

    @classmethod
    def get_benchmark(cls) -> dict:
        if cls.benchmark_cache is None:
            cls.benchmark_cache = run_bidirectional_pha_benchmark()
        return cls.benchmark_cache

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/landing", "/landing.html"):
            body = STATIC_LANDING_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path in ("/", "/workspace", "/workspace.html", "/index.html"):
            body = STATIC_WORKSPACE_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/api/benchmark":
            data = self.get_benchmark()
            body = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path.startswith("/api/scenario/"):
            sc_id = parsed.path.split("/api/scenario/", 1)[1].strip().upper()
            data = self.get_benchmark()
            match = next((s for s in data.get("flagship_scenarios", []) if s["scenario_id"] == sc_id), None)
            if match is None:
                self.send_error(404, f"Scenario {sc_id} not found")
                return
            body = json.dumps(match, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/simulate":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(raw.decode("utf-8"))
            sim_result = simulate_custom_pha_state(payload)
            body = json.dumps(sim_result, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone PHA x SALVAGE-AI Bridge Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), PHABridgeRequestHandler)
    print(f"[PHA x SALVAGE-AI Bridge] Listening on http://{args.host}:{args.port}")
    print(f"  - 3D Showpiece Landing Page: http://{args.host}:{args.port}/landing")
    print(f"  - Live Simulation Workspace: http://{args.host}:{args.port}/workspace")
    server.serve_forever()


if __name__ == "__main__":
    main()
