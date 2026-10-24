# Bidirectional `PHA × SALVAGE-AI` Bridge (`personal-health-agent-bridge`)

> **Standalone Research Prototype — Separate Companion to [`deesatzed/spatial-clinical-router`](https://github.com/deesatzed/spatial-clinical-router)**  
> **Authors & Credits:** Wayne Satz & **Google Science Program** (Research & Systems Architecture Collaboration)  
> Synthesizes Google Research's **"The anatomy of a personal health agent"** (Heydari, Xu, et al., *Nature* 2026, [`doi:10.1038/s41586-026-11161-8`](https://www.nature.com/articles/s41586-026-11161-8)) with the **4-Stage Safe Clinical Decision Architecture (`Spatial Clinical Router` / `SALVAGE-AI`)**.

---

## 1. Bidirectional Architectural Synthesis

### Direction A: How `SALVAGE-AI` Methods Harden Google's Personal Health Agent (`DSA` + `DEA` + `HCA`)

| `SALVAGE-AI` Mechanism | Integration Point in Google's 3-Agent PHA | Empirical Impact (`N = 160` Post-Discharge Benchmark) |
| :--- | :--- | :--- |
| **A1. 4D `storetime` Temporal State Lock (`models.py`)** | Joins continuous wearable telemetry (`t_sync`) with outpatient EHR labs/cultures by portal verification time (`storetime <= t_k`) rather than specimen collection time (`charttime <= t_k`). | Prevents **`+0.1890` artificial AUROC inflation** (`0.8110` strict `storetime` vs. `1.0000` leaky `charttime`) at Day 7 post-discharge when outpatient CRP, BMP, and wound cultures are still pending. |
| **A2. *Drosophila* `240-KC` `Unavailable != Negative` VOI Router (`agents.py`)** | Embedded inside the **Domain Expert Agent (DEA)** (`95.0%` Kenyon-Cell sparsity) to distinguish unmeasured outpatient tests (`MISSING_UNORDERED`) from normal findings. | Achieves **`100.0%` Top-3 missing-workup Recall@3** (`1.0000` vs. `0.6875` in un-gated 3-agent PHA and `0.4562` in a monolithic LLM), prioritizing unmeasured Hallux Toe Pressure (`PHA-03`) or Spot Urine Sodium (`PHA-05`). |
| **A3. Fail-Closed Hernán–Robins Target-Trial Gate (`agents.py`)** | Embedded inside the **Data Science Agent (DSA)** when evaluating behavioral or medication contrasts across observational wearable data. | Blocks **`100.0%` of unidentifiable causal claims** (`NOT_IDENTIFIABLE` when common support $< 70\%$, e.g., step progression during a $+2.6^\circ\text{C}$ plantar thermal flare `PHA-01`) while preserving aligned cardiorenal decongestion utility (`PHA-04`, `RD = -0.131`). |
| **A4. On-Wearable Google Coral NPU (`RV32IMF_Zve32x`) Tier-0 Sentinel (`coral_wearable_sentinel.py`)** | Runs locally on the smartwatch / smart offloading boot (`250 MHz`, `6.40 KB` SRAM, `0.0341 ms`, `3.82 mW`) prior to waking the cloud multi-agent LLM. | Suppresses **`100.0%` of routine benign wearable syncs** (`PHA-02`, `PHA-04`, `PHA-06`) from waking the cloud LLM while maintaining **`100.0%` wake sensitivity** on clinical red-flag flares (`PHA-01`, `PHA-05`). |

---

### Direction B: How Google's 3-Agent PHA (`DSA` + `DEA` + `HCA`) Extends `SALVAGE-AI` Beyond Hospital Discharge

1. **`DataScienceAgent` (DSA):** Tracks post-discharge wearable trajectories (resting heart rate, HRV RMSSD, sleep duration, daily Bluetooth body weight, smart-boot offloading adherence %, and plantar thermal asymmetry $\Delta T$) using personal baseline Z-scores and population percentiles.
2. **`DomainExpertAgent` (DEA):** Interprets DSA trajectories against `IWGDF/IDSA 2023` (post-DFI remission) and `Surviving Sepsis / KDIGO` (post-ICU cardiorenal transition) guidelines with anti-reward-hacking utility alignment.
3. **`HealthCoachAgent` (HCA) + Clinician `NowCard` Escalation Bridge:**
   - On **stable recovery days (`PHA-02`, `PHA-04`, `PHA-06`)**, delivers structured **Motivational Interviewing (`OARS`: Open Question, Affirmation, Reflection, Summary)** and SMART behavioral goals.
   - On **red-flag or high-VOI uncertainty days (`PHA-01`, `PHA-03`, `PHA-05`)**, automatically **halts autonomous lifestyle coaching (`0.0%` unsafe coaching rate vs. `12.5%` in unguarded PHA and `34.0%` in a monolithic LLM)** and mints a cryptographically signed **`sdr.decision.v1` Clinician NowCard** chained in an HMAC-SHA256 ledger.

---

## 2. Companion Academic Manuscript & arXiv Package

The full companion preprint and ready-to-upload arXiv LaTeX package are located in [`PAPER/`](PAPER/):
* **Full Markdown Manuscript:** [`PAPER/MANUSCRIPT_PHA_SALVAGE_BRIDGE.md`](PAPER/MANUSCRIPT_PHA_SALVAGE_BRIDGE.md)
* **Compiled 2-Column PDF:** [`PAPER/arxiv_submission/main.pdf`](PAPER/arxiv_submission/main.pdf)
* **Ready-to-Upload arXiv Tarball:** [`PAPER/arxiv_submission/pha_salvage_bridge_arxiv.tar.gz`](PAPER/arxiv_submission/pha_salvage_bridge_arxiv.tar.gz)
* **Copy-Paste arXiv Submission Metadata:** [`PAPER/arxiv_submission/ARXIV_METADATA.txt`](PAPER/arxiv_submission/ARXIV_METADATA.txt)

---

## 3. Quickstart: Setup, Benchmark, Tests, & Interactive Dashboard

**Zero third-party dependencies required** (runs out-of-the-box on Python `3.10+` standard library).

```bash
# 1. Clone the repository
git clone https://github.com/deesatzed/personal-health-agent-bridge.git
cd personal-health-agent-bridge

# 2. Run the 5-Test Automated Verification Suite & Manuscript Consistency Auditor
python3 tests/test_pha_salvage_bridge.py -v
python3 scripts/verify_pha_manuscript.py

# 3. Regenerate the N=160 Bidirectional Benchmark (data/pha_salvage_bidirectional_benchmark.json)
python3 src/pha_salvage_bridge/benchmark.py

# 4. Launch the Standalone Interactive Web Dashboard (http://127.0.0.1:8790)
python3 src/pha_salvage_bridge/server.py
```

---

## 4. Repository Structure

```text
personal-health-agent-bridge/
├── README.md
├── PAPER/
│   ├── MANUSCRIPT_PHA_SALVAGE_BRIDGE.md           # Full companion academic manuscript
│   └── arxiv_submission/                          # Ready-to-upload arXiv LaTeX bundle & compiled PDF
│       ├── main.tex
│       ├── main.pdf
│       ├── references.bib
│       ├── ARXIV_METADATA.txt
│       └── pha_salvage_bridge_arxiv.tar.gz
├── data/
│   └── pha_salvage_bidirectional_benchmark.json   # N=160 post-discharge benchmark & 6 flagship scenarios
├── scripts/
│   └── verify_pha_manuscript.py                   # Automated benchmark-to-manuscript consistency auditor
├── src/
│   └── pha_salvage_bridge/
│       ├── __init__.py
│       ├── models.py                              # 4D Time-Locked Wearable + Outpatient EHR State
│       ├── coral_wearable_sentinel.py             # On-Wearable Coral NPU (RV32IMF_Zve32x, 3.82 mW) Gate
│       ├── agents.py                              # DSA + DEA + HCA + Fail-Closed NowCard Orchestrator
│       ├── benchmark.py                           # N=160 3-Arm Post-Discharge Evaluation Engine
│       └── server.py                              # Standalone Interactive Dashboard (Port 8790)
└── tests/
    └── test_pha_salvage_bridge.py                 # 5-test verification suite
```
