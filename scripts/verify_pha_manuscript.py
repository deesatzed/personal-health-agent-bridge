#!/usr/bin/env python3
"""
Automated Benchmark-to-Manuscript Consistency Auditor for personal-health-agent-bridge.
Verifies that all quantitative metrics and Google Science Program credits in
PAPER/MANUSCRIPT_PHA_SALVAGE_BRIDGE.md, PAPER/arxiv_submission/main.tex,
PAPER/arxiv_submission/ARXIV_METADATA.txt, and README.md match
data/pha_salvage_bidirectional_benchmark.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK_JSON = ROOT / "data" / "pha_salvage_bidirectional_benchmark.json"
MANUSCRIPT_MD = ROOT / "PAPER" / "MANUSCRIPT_PHA_SALVAGE_BRIDGE.md"
MAIN_TEX = ROOT / "PAPER" / "arxiv_submission" / "main.tex"
ARXIV_META = ROOT / "PAPER" / "arxiv_submission" / "ARXIV_METADATA.txt"
README_MD = ROOT / "README.md"


def main() -> int:
    data = json.loads(BENCHMARK_JSON.read_text(encoding="utf-8"))
    md_text = MANUSCRIPT_MD.read_text(encoding="utf-8")
    tex_text = MAIN_TEX.read_text(encoding="utf-8")
    meta_text = ARXIV_META.read_text(encoding="utf-8")
    readme_text = README_MD.read_text(encoding="utf-8")

    leakage = data["outpatient_timestamp_leakage_audit"]
    coral = data["coral_npu_wearable_sentinel_audit"]
    arms = data["three_arm_architecture_comparison"]

    required_token_groups = [
        ["Google Science Program"],
        ["10.1038/s41586-026-11161-8"],
        [f"{leakage['strict_storetime_auroc']:.4f}"],
        [f"{leakage['naive_charttime_leaked_auroc']:.4f}"],
        [f"{leakage['auroc_inflation_delta']:.4f}"],
        [f"{coral['simulated_latency_ms']:.4f}"],
        [f"{coral['simulated_power_mw']:.2f}"],
        [f"{coral['sram_footprint_kb']:.2f}"],
        [
            f"{arms['Arm_1_Monolithic_Ungated_LLM']['missing_workup_voi_recall_at_3']:.4f}",
            f"{arms['Arm_1_Monolithic_Ungated_LLM']['missing_workup_voi_recall_at_3'] * 100:.2f}%",
        ],
        [
            f"{arms['Arm_2_Standard_3Agent_PHA_No_SALVAGE_Guards']['missing_workup_voi_recall_at_3']:.4f}",
            f"{arms['Arm_2_Standard_3Agent_PHA_No_SALVAGE_Guards']['missing_workup_voi_recall_at_3'] * 100:.2f}%",
        ],
        [
            f"{arms['Arm_3_Bidirectional_PHA_x_SALVAGE_AI_Bridge']['missing_workup_voi_recall_at_3']:.4f}",
            f"{arms['Arm_3_Bidirectional_PHA_x_SALVAGE_AI_Bridge']['missing_workup_voi_recall_at_3'] * 100:.2f}%",
            f"{arms['Arm_3_Bidirectional_PHA_x_SALVAGE_AI_Bridge']['missing_workup_voi_recall_at_3'] * 100:.1f}%",
        ],
        [f"{arms['Arm_1_Monolithic_Ungated_LLM']['unsafe_coaching_during_acute_flare_pct']:.1f}%"],
        [f"{arms['Arm_2_Standard_3Agent_PHA_No_SALVAGE_Guards']['unsafe_coaching_during_acute_flare_pct']:.1f}%"],
        [f"{arms['Arm_3_Bidirectional_PHA_x_SALVAGE_AI_Bridge']['unsafe_coaching_during_acute_flare_pct']:.1f}%"],
    ]

    for doc_name, doc_text in [
        ("MANUSCRIPT_PHA_SALVAGE_BRIDGE.md", md_text),
        ("main.tex", tex_text),
        ("ARXIV_METADATA.txt", meta_text),
        ("README.md", readme_text),
    ]:
        for group in required_token_groups:
            matched = False
            for tok in group:
                tex_tok = tok.replace("%", "\\%")
                if tok in doc_text or tex_tok in doc_text:
                    matched = True
                    break
            if not matched:
                print(f"[VERIFY FAIL] Missing token group {group} in {doc_name}", file=sys.stderr)
                return 1

    print("[VERIFY PASS] All PHA x SALVAGE-AI benchmark metrics and Google Science Program credits verified across Markdown, LaTeX, Metadata, and README.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
