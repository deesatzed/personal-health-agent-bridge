"""
Standalone HTTP Server & Interactive Dashboard for `PHA × SALVAGE-AI` Bridge (`server.py`).

Runs on port 8790 (`http://127.0.0.1:8790`) so it never conflicts with the frozen
`spatial-clinical-router` server on port 8780.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pha_salvage_bridge.benchmark import run_bidirectional_pha_benchmark


HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PHA × SALVAGE-AI Bridge — Nature s41586-026-11161-8 Bidirectional Synthesis</title>
  <style>
    :root {
      --bg: #030712; --card: #0f172a; --border: rgba(56,189,248,0.25);
      --text: #f8fafc; --muted: #94a3b8; --cyan: #22d3ee; --emerald: #10b981;
      --amber: #f59e0b; --crimson: #ef4444; --violet: #a855f7;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 24px 36px; line-height: 1.5; }
    header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
    h1 { font-size: 20px; font-weight: 800; letter-spacing: -0.02em; }
    .badge { display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; }
    .b-cyan { background: rgba(34,211,238,0.15); color: var(--cyan); border: 1px solid rgba(34,211,238,0.4); }
    .b-emerald { background: rgba(16,185,129,0.15); color: var(--emerald); border: 1px solid rgba(16,185,129,0.4); }
    .b-crimson { background: rgba(239,68,68,0.15); color: var(--crimson); border: 1px solid rgba(239,68,68,0.4); }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
    .kpi-val { font-size: 26px; font-weight: 800; color: var(--cyan); font-family: monospace; }
    .kpi-lbl { font-size: 12px; color: var(--muted); margin-top: 4px; }
    .layout { display: grid; grid-template-columns: 320px 1fr; gap: 20px; }
    .sc-btn { width: 100%; text-align: left; background: rgba(15,23,42,0.8); border: 1px solid rgba(148,163,184,0.2); color: var(--text); padding: 12px; border-radius: 10px; margin-bottom: 8px; cursor: pointer; }
    .sc-btn.active { border-color: var(--cyan); background: rgba(34,211,238,0.1); }
    .agent-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 14px; }
    pre { background: #020617; padding: 10px; border-radius: 8px; font-size: 11px; overflow-x: auto; color: #cbd5e1; border: 1px solid rgba(148,163,184,0.15); margin-top: 8px; }
  </style>
</head>
<body>
  <header>
    <div>
      <span class="badge b-cyan">STANDALONE PROTOTYPE · SEPARATE FROM SPATIAL-CLINICAL-ROUTER</span>
      <h1 style="margin-top:6px;">PHA × SALVAGE-AI Bridge · Nature (s41586-026-11161-8) Bidirectional Synthesis</h1>
    </div>
    <div id="statusPill" class="badge b-emerald">N=160 Benchmark Loaded</div>
  </header>

  <div class="kpi-grid" id="kpiGrid"></div>

  <div class="layout">
    <div id="scenarioList"></div>
    <div class="card" id="scenarioDetail">Loading benchmark...</div>
  </div>

  <script>
    let BENCH = null;
    function renderScenario(idx) {
      const sc = BENCH.flagship_scenarios[idx];
      document.querySelectorAll('.sc-btn').forEach((b, i) => b.classList.toggle('active', i === idx));
      const c = sc.coral_sentinel;
      const dsa = sc.dsa_output;
      const dea = sc.dea_output;
      const hca = sc.hca_output;
      document.getElementById('scenarioDetail').innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span class="badge b-cyan">${sc.scenario_id} · ${sc.cohort_domain} (Landmark +${sc.t_landmark_hours}h)</span>
          <span style="font-family:monospace;font-size:11px;color:var(--muted);">Merkle: ${sc.merkle_root.slice(0,20)}...</span>
        </div>
        <h2 style="font-size:18px;margin-bottom:8px;">${sc.title}</h2>
        <p style="font-size:13px;color:#cbd5e1;margin-bottom:14px;">${sc.clinical_story}</p>
        <div class="agent-grid">
          <div class="card">
            <span class="badge b-cyan">TIER-0 · GOOGLE CORAL NPU WEARABLE SENTINEL</span>
            <p style="font-size:12px;margin-top:8px;"><strong>Wake Cloud 3-Agent PHA:</strong> ${c.wake_cloud_orchestrator ? '<span style="color:var(--crimson)">YES (WAKE)</span>' : '<span style="color:var(--emerald)">NO (CLOUD SLEEPS)</span>'}</p>
            <p style="font-size:12px;"><strong>Latency / Power / SRAM:</strong> ${c.latency_ms} ms · ${c.active_power_mw} mW · ${c.sram_kb} KB (${c.kc_sparsity_pct}% KC Sparsity)</p>
            <p style="font-size:11px;color:var(--muted);margin-top:4px;">${c.wake_reason}</p>
          </div>
          <div class="card">
            <span class="badge b-cyan">AGENT 1 · DATA SCIENCE AGENT (DSA) + TARGET-TRIAL GATE</span>
            <p style="font-size:12px;margin-top:8px;"><strong>30d Relapse Risk:</strong> ${(dsa.predicted_30d_readmission_risk*100).toFixed(1)}% (${dsa.leakage_rows_blocked} future storetime rows masked)</p>
            <p style="font-size:12px;"><strong>Target-Trial Gate (${dsa.target_trial_contrast.trial_id}):</strong> <code>${dsa.target_trial_contrast.gate_status}</code> (Overlap ${dsa.target_trial_contrast.common_support_pct}%)</p>
            <p style="font-size:11px;color:var(--muted);margin-top:4px;">${dsa.target_trial_contrast.rationale}</p>
          </div>
          <div class="card">
            <span class="badge b-emerald">AGENT 2 · DOMAIN EXPERT AGENT (DEA) + 240-KC VOI ROUTER</span>
            <p style="font-size:12px;margin-top:8px;"><strong>Escalation Urgency:</strong> <code>${dea.escalation_urgency}</code></p>
            <p style="font-size:11px;color:#cbd5e1;margin-top:4px;">${dea.reward_alignment_note}</p>
            <pre>${JSON.stringify(dea.top_voi_missing_workup, null, 2)}</pre>
          </div>
          <div class="card">
            <span class="badge ${hca.coaching_mode.includes('HALTED') ? 'b-crimson' : 'b-emerald'}">AGENT 3 · HEALTH COACH AGENT (HCA) + SDR NOWCARD BRIDGE</span>
            <p style="font-size:12px;margin-top:8px;"><strong>Mode:</strong> <code>${hca.coaching_mode}</code></p>
            <p style="font-size:12px;margin-top:4px;"><strong>SMART Goal:</strong> ${hca.smart_goal}</p>
            <pre>${JSON.stringify(hca.clinician_nowcard_handoff || hca.mi_strategy_oars, null, 2)}</pre>
          </div>
        </div>
      `;
    }
    fetch('/api/benchmark').then(r => r.json()).then(data => {
      BENCH = data;
      const lk = data.outpatient_timestamp_leakage_audit;
      const cn = data.coral_npu_wearable_sentinel_audit;
      const a3 = data.three_arm_architecture_comparison.Arm_3_Bidirectional_PHA_x_SALVAGE_AI_Bridge;
      document.getElementById('kpiGrid').innerHTML = `
        <div class="card"><div class="kpi-val">+${lk.auroc_inflation_delta.toFixed(4)}</div><div class="kpi-lbl">Outpatient Lookahead Leakage Caught (${lk.strict_storetime_auroc} Strict vs ${lk.naive_charttime_leaked_auroc} Leaky)</div></div>
        <div class="card"><div class="kpi-val">${(a3.missing_workup_voi_recall_at_3*100).toFixed(1)}%</div><div class="kpi-lbl">240-KC Missing-Workup VOI Recall@3 inside DEA</div></div>
        <div class="card"><div class="kpi-val">${cn.routine_benign_syncs_suppressed_pct}%</div><div class="kpi-lbl">Routine Wearable Syncs Suppressed on Coral NPU (${cn.simulated_power_mw} mW)</div></div>
        <div class="card"><div class="kpi-val">${a3.unsafe_coaching_during_acute_flare_pct.toFixed(1)}%</div><div class="kpi-lbl">Unsafe Autonomous Coaching During Acute Flares (100% NowCard Escalation)</div></div>
      `;
      document.getElementById('scenarioList').innerHTML = data.flagship_scenarios.map((s, i) => `
        <button class="sc-btn ${i===0?'active':''}" onclick="renderScenario(${i})">
          <div style="font-size:11px;color:var(--cyan);font-weight:700;">${s.scenario_id} · ${s.cohort_domain}</div>
          <div style="font-size:13px;font-weight:700;margin-top:3px;">${s.title}</div>
        </button>
      `).join('');
      renderScenario(0);
    });
  </script>
</body>
</html>
"""


class PHABridgeRequestHandler(BaseHTTPRequestHandler):
    benchmark_cache = None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = HTML_DASHBOARD.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/api/benchmark":
            if PHABridgeRequestHandler.benchmark_cache is None:
                PHABridgeRequestHandler.benchmark_cache = run_bidirectional_pha_benchmark()
            body = json.dumps(PHABridgeRequestHandler.benchmark_cache, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run standalone PHA x SALVAGE-AI Bridge server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), PHABridgeRequestHandler)
    print(f"[PHA x SALVAGE-AI Bridge] Listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
