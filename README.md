# Bidirectional `PHA × SALVAGE-AI` Bridge (`personal-health-agent-bridge`)

**Hardening Multi-Agent Personal Health Systems Across the Inpatient-to-Home Continuum via 4D Time-Locked EHR States, Fail-Closed Target Trials, and Sub-5 mW Wearable Sentinels**  
**Authors & Credits:** Wayne Satz & **Google Science Program** (Research & Systems Architecture Collaboration)

[![Tests](https://img.shields.io/badge/tests-5%2F5%20passing-10b981)](#step-4-run-the-automated-test-suite--manuscript-consistency-auditor)
[![Manuscript Auditor](https://img.shields.io/badge/manuscript%20auditor-VERIFY%20PASS-22d3ee)](#step-4-run-the-automated-test-suite--manuscript-consistency-auditor)
[![Google Science Program](https://img.shields.io/badge/collaboration-Google%20Science%20Program-3b82f6)](PAPER/MANUSCRIPT_PHA_SALVAGE_BRIDGE.md)
[![Nature Synthesis](https://img.shields.io/badge/Nature%202026%20Synthesis-doi%3A10.1038%2Fs41586--026--11161--8-c084fc)](https://www.nature.com/articles/s41586-026-11161-8)
[![Wearable Coral NPU](https://img.shields.io/badge/Coral%20NPU%20Edge-RV32IMF__Zve32x%20%C2%B7%203.82mW%20%C2%B7%206.40KB-10b981)](#43-tier-0-wearable-google-coral-npu-rv32imf_zve32x-edge-sentinel-performance)
[![Dependencies](https://img.shields.io/badge/dependencies-Python%203.10%2B%20Stdlib%20Only-f59e0b)](#31-prerequisites--zero-dependency-design)

> **📝 Full Academic Preprint #2 (`IMRaD` Format, PDF & arXiv Bundle):** [**`PAPER/MANUSCRIPT_PHA_SALVAGE_BRIDGE.md`**](PAPER/MANUSCRIPT_PHA_SALVAGE_BRIDGE.md) · [**`PAPER/arxiv_submission/main.pdf`**](PAPER/arxiv_submission/main.pdf) · [**`PAPER/arxiv_submission/pha_salvage_bridge_arxiv.tar.gz`**](PAPER/arxiv_submission/pha_salvage_bridge_arxiv.tar.gz)  
> **🌐 Interactive 3D Showpiece Landing Page & Multi-Agent Explorer:** [**`src/pha_salvage_bridge/static/landing.html`**](src/pha_salvage_bridge/static/landing.html) (`http://127.0.0.1:8790/landing` · GitHub Pages mirror at [**`docs/index.html`**](docs/index.html))  
> **🤝 Companion Preprint #1 (`Spatial Clinical Router` / `SALVAGE-AI` Inpatient Architecture):** [**`deesatzed/spatial-clinical-router`**](https://github.com/deesatzed/spatial-clinical-router)  
> **📖 Reference Architecture:** Heydari, Xu, et al., *"The anatomy of a personal health agent"*, *Nature* (2026), [`doi:10.1038/s41586-026-11161-8`](https://www.nature.com/articles/s41586-026-11161-8)

---

## Table of Contents

1. [Executive Overview: Bridging Acute Inpatient Triage and Consumer Personal Health Agents](#1-executive-overview-bridging-acute-inpatient-triage-and-consumer-personal-health-agents)
2. [Bidirectional Architectural Synthesis (`Directions A & B`)](#2-bidirectional-architectural-synthesis-directions-a--b)
3. [Step-by-Step Setup, Execution & Reproducibility Guide](#3-step-by-step-setup-execution--reproducibility-guide)
   - [3.1 Prerequisites & Zero-Dependency Design](#31-prerequisites--zero-dependency-design)
   - [3.2 Step 1: Clone & Inspect Repository Layout](#32-step-1-clone--inspect-repository-layout)
   - [3.3 Step 2: Launch the Interactive 3D Landing Page & Multi-Agent Explorer (`Port 8790`)](#33-step-2-launch-the-interactive-3d-landing-page--multi-agent-explorer-port-8790)
   - [3.4 Step 3: Regenerate the Deterministic `N = 160` Post-Discharge Benchmark](#34-step-3-regenerate-the-deterministic-n--160-post-discharge-benchmark)
   - [3.5 Step 4: Run the Automated Test Suite & Manuscript Consistency Auditor](#35-step-4-run-the-automated-test-suite--manuscript-consistency-auditor)
   - [3.6 Step 5: Query the Local Multi-Agent REST API Endpoints Directly](#36-step-5-query-the-local-multi-agent-rest-api-endpoints-directly)
4. [Empirical Benchmark Results (`N = 160` Post-Discharge Trajectories & 6 Flagship Scenarios)](#4-empirical-benchmark-results-n--160-post-discharge-trajectories--6-flagship-scenarios)
5. [Repository Structure](#5-repository-structure)

---

## 1. Executive Overview: Bridging Acute Inpatient Triage and Consumer Personal Health Agents

Consumer-facing multi-agent personal health systems—most notably the **Personal Health Agent (PHA)** architecture introduced by Heydari, Xu, et al. (*Nature*, 2026; `doi:10.1038/s41586-026-11161-8`), which coordinates a **Data Science Agent (DSA)**, **Domain Expert Agent (DEA)**, and **Health Coach Agent (HCA)**—excel at longitudinal wearable analytics and behavioral coaching. However, when deployed across the high-risk **inpatient-to-home post-discharge transition** (Days 1–90 following acute hospitalization for diabetic foot limb salvage or sepsis/cardiorenal syndrome), unguarded consumer agents face four clinical safety hazards:

1. **Outpatient `charttime` vs. `storetime` Look-Ahead Leakage:** Joining continuous wearable streams ($t_{\text{sync}}$) with outpatient EHR labs/cultures by specimen collection time ($t_{\text{chart}} \le t_k$) rather than patient-portal verification time ($t_{\text{store}} \le t_k$) leaks delayed CRP, BMP, and send-out wound culture results.
2. **Implicit Negative Imputation (`Unavailable == Negative`):** Treating unordered outpatient perfusion checks (`pedal_doppler_toe_pressure_mmhg`) or natriuresis labs (`spot_urine_sodium_mmol_l`) as normal rather than routing them as high-Value-of-Information (`VOI`) diagnostic queries.
3. **Observational Healthy-Adherer Confounding & Positivity Violations:** Recommending step progression during an acute $+2.6^\circ\text{C}$ plantar thermal flare (`PHA-01`) or autonomous fluid/diuretic adjustments without verified electrolytes (`PHA-05`).
4. **Always-On Cloud LLM Power & Privacy Drain:** Waking a 4-call cloud LLM orchestrator on every routine smartwatch or smart-boot Bluetooth sync.

Conversely, our inpatient **4-Stage Spatial Clinical Router (`SALVAGE-AI`)** terminates at hospital discharge. This standalone repository implements and validates the **Bidirectional `PHA × SALVAGE-AI` Bridge**, unifying both architectures across the 90-day inpatient-to-home continuum.

---

## 2. Bidirectional Architectural Synthesis (`Directions A & B`)

### Direction A (`SALVAGE-AI` $\rightarrow$ `PHA`): Four Clinical Safety Guards for Google's 3-Agent PHA

| `SALVAGE-AI` Mechanism | Integration Point in Google's 3-Agent PHA | Empirical Impact (`N = 160` Post-Discharge Benchmark) |
| :--- | :--- | :--- |
| **A1. 4D `storetime` Temporal State Lock ([`models.py`](src/pha_salvage_bridge/models.py))** | Joins continuous wearable telemetry (`t_sync_hours`) with outpatient EHR labs/cultures by portal verification time (`t_store_hours <= t_k`) rather than specimen collection time (`t_chart_hours <= t_k`), sealing each landmark with a SHA-256 Merkle root. | Prevents **`+0.1890` artificial AUROC inflation** (`0.8110` strict `storetime` vs. `1.0000` leaky `charttime`) at Day 7 post-discharge when outpatient CRP, BMP, and wound cultures are still pending. |
| **A2. *Drosophila* `240-KC` `Unavailable != Negative` VOI Router ([`agents.py`](src/pha_salvage_bridge/agents.py))** | Embedded inside the **Domain Expert Agent (DEA)** (`95.0%` Kenyon-Cell sparsity) to distinguish unmeasured outpatient tests (`MISSING_UNORDERED`) and pending labs (`PENDING_AT_LANDMARK`) from normal findings. | Achieves **`100.0%` Top-3 missing-workup Recall@3** (`1.0000` vs. `0.6875` in un-gated 3-agent PHA and `0.4562` in a monolithic LLM), prioritizing unmeasured Hallux Toe Pressure (`PHA-03`) or Spot Urine Sodium (`PHA-05`). |
| **A3. Fail-Closed Hernán–Robins Target-Trial Gate ([`agents.py`](src/pha_salvage_bridge/agents.py))** | Embedded inside the **Data Science Agent (DSA)** when evaluating behavioral or medication contrasts across observational wearable data (`Overlap >= 70%`, `|SMD| <= 0.12`, plus Manski bounds & E-values). | Blocks **`100.0%` of unidentifiable causal claims** (`NOT_IDENTIFIABLE` when common support $< 70\%$, e.g., step progression during a $+2.6^\circ\text{C}$ plantar thermal flare `PHA-01`) while preserving aligned cardiorenal decongestion utility (`PHA-04`, `RD = -0.131`). |
| **A4. On-Wearable Google Coral NPU (`RV32IMF_Zve32x`) Tier-0 Sentinel ([`coral_wearable_sentinel.py`](src/pha_salvage_bridge/coral_wearable_sentinel.py))** | Runs locally on the smartwatch / smart offloading boot (`250 MHz`, `6.40 KB` SRAM, `0.0341 ms`, `3.82 mW`) prior to waking the cloud multi-agent LLM. | Suppresses **`100.0%` of routine benign wearable syncs** (`PHA-02`, `PHA-04`, `PHA-06`) from waking the cloud LLM while maintaining **`100.0%` wake sensitivity** on clinical red-flag flares (`PHA-01`, `PHA-05`). |

### Direction B (`PHA` $\rightarrow$ `SALVAGE-AI`): Extending Inpatient Anti-Reward-Hacking Triage into Home Recovery

1. **`DataScienceAgent` (DSA):** Tracks post-discharge wearable trajectories (resting heart rate, HRV RMSSD, sleep duration, daily Bluetooth body weight $\Delta\text{Weight}_{72\text{h}}$, smart-boot offloading adherence %, and plantar thermal asymmetry $\Delta T_{\text{plantar}}$) using personal baseline Z-scores and population percentiles.
2. **`DomainExpertAgent` (DEA):** Interprets DSA trajectories against `IWGDF/IDSA 2023` (post-DFI remission) and `Surviving Sepsis / KDIGO` (post-ICU cardiorenal transition) guidelines with anti-reward-hacking utility alignment (`+3.00` functional salvage utility for minor ray resection with intact heel/arch; `+2.85` utility for permissive hypercreatininemia during brisk natriuresis $\text{UNa} > 70\text{ mmol/L}$).
3. **`HealthCoachAgent` (HCA) + Clinician `NowCard` Escalation Bridge:**
   - On **stable recovery days (`PHA-02`, `PHA-03`, `PHA-04`, `PHA-06`)**, delivers structured **Motivational Interviewing (`OARS`: Open Question, Affirmation, Reflection, Summary)** and 7-day SMART behavioral goals.
   - On **acute clinical flare days (`PHA-01`, `PHA-05`)**, automatically **halts autonomous lifestyle coaching (`0.0%` unsafe coaching rate vs. `12.5%` in unguarded PHA and `34.0%` in a monolithic LLM)** and mints a cryptographically signed **`sdr.decision.v1` Clinician NowCard** chained in an HMAC-SHA256 ledger.

---

## 3. Step-by-Step Setup, Execution & Reproducibility Guide

### 3.1 Prerequisites & Zero-Dependency Design
- **Operating System:** macOS, Linux, or Windows (WSL2).
- **Python Version:** **Python `3.10+`** (tested on Python `3.10` through `3.15`).
- **External Dependencies:** **None (`0` third-party packages required).** Runs 100% on the Python standard library (`json`, `math`, `hashlib`, `hmac`, `http.server`, `unittest`).

### 3.2 Step 1: Clone & Inspect Repository Layout
```bash
git clone https://github.com/deesatzed/personal-health-agent-bridge.git
cd personal-health-agent-bridge
```

### 3.3 Step 2: Launch the Interactive 3D Landing Page & Multi-Agent Explorer (`Port 8790`)
The standalone HTTP server runs on port `8790` (so it never conflicts with `spatial-clinical-router` on port `8780`):
```bash
python3 src/pha_salvage_bridge/server.py
```
Then open your browser to:
- **Interactive 3D Showpiece Landing Page & Scenario Explorer:** [`http://127.0.0.1:8790/landing`](http://127.0.0.1:8790/landing) (also served at [`http://127.0.0.1:8790/`](http://127.0.0.1:8790/))
- **JSON Benchmark Endpoint:** [`http://127.0.0.1:8790/api/benchmark`](http://127.0.0.1:8790/api/benchmark)

### 3.4 Step 3: Regenerate the Deterministic `N = 160` Post-Discharge Benchmark
```bash
PYTHONPATH=src python3 src/pha_salvage_bridge/benchmark.py
```
This deterministically regenerates [`data/pha_salvage_bidirectional_benchmark.json`](data/pha_salvage_bidirectional_benchmark.json) (`N = 160` trajectories: `80` `POST_DFI_SALVAGE` + `80` `POST_SEPSIS_CARDIORENAL`, fixed seed `20261024`) and prints the full 3-arm audit summary.

### 3.5 Step 4: Run the Automated Test Suite & Manuscript Consistency Auditor
```bash
# 1. Run the 5-test unit & integration suite
PYTHONPATH=src python3 tests/test_pha_salvage_bridge.py -v

# 2. Run the automated benchmark-to-manuscript consistency auditor
python3 scripts/verify_pha_manuscript.py
```
Expected output:
```text
Ran 5 tests in 0.053s — OK
[VERIFY PASS] All PHA x SALVAGE-AI benchmark metrics and Google Science Program credits verified across Markdown, LaTeX, Metadata, and README.
```

### 3.6 Step 5: Query the Local Multi-Agent REST API Endpoints Directly
While `server.py` is running on port `8790`:
```bash
# Fetch the full N=160 benchmark summary
curl -s http://127.0.0.1:8790/api/benchmark | python3 -m json.tool | head -n 40

# Fetch a single flagship scenario (e.g., PHA-01 or PHA-05)
curl -s http://127.0.0.1:8790/api/scenario/PHA-01 | python3 -m json.tool
```

---

## 4. Empirical Benchmark Results (`N = 160` Post-Discharge Trajectories & 6 Flagship Scenarios)

### 4.1 Outpatient `charttime` vs. `storetime` Temporal Leakage Audit (`Day 7 Landmark, t_k = 168.0h`)

| Evaluation Protocol | Timestamp Filter Applied at $t_k = 168.0\text{h}$ | 30-Day Readmission / Relapse AUROC | Optimistic Leakage Inflation ($\Delta\text{AUROC}$) | Delayed Outpatient Labs Masked (%) |
| :--- | :--- | :---: | :---: | :---: |
| **Strict 4D State Lock (`PHA × SALVAGE-AI`)** | $t_{\text{store}}(e_i) \le 168.0\text{h}$ | **`0.8110`** | Baseline (Zero Leakage) | **`100.0%`** |
| **Naive Retrospective Join (`Leaked charttime`)** | $t_{\text{chart}}(e_i) \le 168.0\text{h}$ | `1.0000` | **`+0.1890`** | `0.0%` |

### 4.2 Three-Arm Architecture Comparison ($N = 160$: $n = 80$ `POST_DFI_SALVAGE` + $n = 80$ `POST_SEPSIS_CARDIORENAL`)

| Architectural Arm | Exposed to Outpatient `charttime` Leakage? | Missing-Workup Top-3 VOI Recall@3 | Unidentifiable Causal Claims Blocked (%) | Unsafe Lifestyle Coaching During Acute Flare (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Arm 1: Monolithic Ungated LLM** | Yes (`Leaked`) | `0.4562` (`45.6%`) | `0.0%` | `34.0%` |
| **Arm 2: Standard 3-Agent PHA (No `SALVAGE` Guards)** | Yes (`Leaked`) | `0.6875` (`68.8%`) | `0.0%` | `12.5%` |
| **Arm 3: Bidirectional `PHA × SALVAGE-AI` Bridge** | **No (`storetime` Locked)** | **`1.0000` (`100.0%`)** | **`100.0%`** | **`0.0%`** |

### 4.3 Tier-0 Wearable Google Coral NPU (`RV32IMF_Zve32x`) Edge Sentinel Performance

| Hardware / Clinical Gate Metric | Value | Architectural Significance |
| :--- | :---: | :--- |
| **Target Edge ISA & Clock** | `RV32IMF_Zve32x` @ `250 MHz` | Smartwatch / smart-offloading-boot ultra-low-power coprocessor envelope |
| **On-Chip SRAM Footprint** | **`6.40 KB`** | `240x14` `INT8` projection weights + thresholds fit in tightly coupled SRAM |
| **Kenyon-Cell Sparsity (`APL k-WTA`)** | **`95.0%`** ($12 / 240$ active) | Prevents feature collision between consumer PPG and missing EHR indicators |
| **Inference Latency per Sync** | **`0.0341 ms`** ($34.1\ \mu\text{s}$) | Real-time edge filtering prior to Bluetooth/cellular cloud transmission |
| **Active Edge Power Envelope** | **`3.82 mW`** | Eliminates continuous multi-agent cloud LLM token and radio drain |
| **Routine Benign Syncs Suppressed on Edge** | **`100.0%`** | All stable recovery syncs (`PHA-02`, `PHA-04`, `PHA-06`) sleep at the edge |
| **Clinical Red-Flag Wake Sensitivity** | **`100.0%`** | Zero missed acute thermal, weight-surge, or sympathetic decompensation flares |

### 4.4 Six Flagship Post-Discharge Inpatient-to-Home Scenarios (`PHA-01` – `PHA-06`)

| ID | Cohort & Scenario ($t_k$) | Coral NPU Edge Decision | DSA Target-Trial Gate & Risk ($R_{30\text{d}}$) | DEA Top-1 VOI Missing Workup (`If-Wrong` Interval) | HCA Mode & `sdr.decision.v1` NowCard |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`PHA-01`** | **`POST_DFI_SALVAGE` ($168\text{h}$):** $+2.6^\circ\text{C}$ plantar thermal flare; CRP ($172\text{h}$) & wound swab ($212\text{h}$) pending (`2` leaked rows blocked) | **WAKE CLOUD** (`IMMEDIATE_CLINICAL_ESCALATION`) | `NOT_IDENTIFIABLE` (Overlap `31.4%`); $R_{30\text{d}} = 51.1\%$ | `pedal_doppler_toe_pressure_mmhg` (`VOI = 0.95`, `[0.281, 0.834]`) | **`HALTED_FOR_CLINICIAN_ESCALATION`** (`STAT_PROVIDER_CROSSROADS` NowCard `8cd8f93c...`) |
| **`PHA-02`** | **`POST_DFI_SALVAGE` ($336\text{h}$):** Clean 2nd-ray resection remission; $94\%$ smart-boot adherence, $\Delta T = 0.5^\circ\text{C}$, RHR $68\text{ bpm}$ | **SUPPRESSED ON EDGE** (`Cloud LLM Sleeps`) | `EXPLORATORY_FEASIBLE` (Overlap `94.2%`, `RD = -0.164`); $R_{30\text{d}} = 12.0\%$ | `wound_probe_or_culture` (`VOI = 0.92`, `[0.066, 0.432]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + $+3.00$ Salvage Utility) |
| **`PHA-03`** | **`POST_DFI_SALVAGE` ($240\text{h}$):** Prior calcified inpatient $\text{ABI} = 1.42$; unordered outpatient hallux toe pressure & subclinical $\Delta T = 1.8^\circ\text{C}$ drift | **WAKE CLOUD** (`SUBCLINICAL_PHYSIOLOGICAL_DRIFT`) | `EXPLORATORY_FEASIBLE` (Overlap `94.2%`, `RD = -0.164`); $R_{30\text{d}} = 23.6\%$ | `pedal_doppler_toe_pressure_mmhg` (`VOI = 0.95`, `[0.130, 0.559]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + High-VOI Perfusion Alert) |
| **`PHA-04`** | **`POST_SEPSIS_CARDIORENAL` ($120\text{h}$):** $-1.8\text{ kg}$ weight loss on oral torsemide; $\text{Cr } 1.55 \rightarrow 1.82\text{ mg/dL}$ with brisk $\text{UNa} = 84\text{ mmol/L}$ | **SUPPRESSED ON EDGE** (`Cloud LLM Sleeps`) | `EXPLORATORY_FEASIBLE` (Overlap `96.0%`, `RD = -0.131`); $R_{30\text{d}} = 5.7\%$ | `venous_pocus_vexus_grade` (`VOI = 0.91`, `[0.032, 0.367]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + Permissive Hypercreatininemia Guard) |
| **`PHA-05`** | **`POST_SEPSIS_CARDIORENAL` ($168\text{h}$):** Acute $+2.5\text{ kg}$ fluid surge in $72\text{h}$, RHR $101\text{ bpm}$, HRV $18\text{ ms}$; BMP pending (`2` leaked rows blocked), $\text{UNa}$ unordered | **WAKE CLOUD** (`IMMEDIATE_CLINICAL_ESCALATION`) | `NOT_IDENTIFIABLE` (Overlap `28.5%`); $R_{30\text{d}} = 58.3\%$ | `serum_creatinine_mg_dl` (`VOI = 0.97`, `[0.321, 0.913]`) | **`HALTED_FOR_CLINICIAN_ESCALATION`** (`STAT_PROVIDER_CROSSROADS` NowCard `30e1db36...`) |
| **`PHA-06`** | **`POST_SEPSIS_CARDIORENAL` ($240\text{h}$):** Stable euvolemic recovery ($\Delta\text{Weight} = -0.1\text{ kg}$, RHR $66\text{ bpm}$, HRV $48\text{ ms}$, verified $\text{Cr } 0.95\text{ mg/dL}$) | **SUPPRESSED ON EDGE** (`Cloud LLM Sleeps`) | `EXPLORATORY_FEASIBLE` (Overlap `96.0%`, `RD = -0.131`); $R_{30\text{d}} = 10.4\%$ | `spot_urine_sodium_mmol_l` (`VOI = 0.96`, `[0.057, 0.431]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + Routine Follow-up Maintenance) |

---

## 5. Repository Structure

```text
personal-health-agent-bridge/
├── README.md
├── docs/
│   └── index.html                                 # GitHub Pages Interactive 3D Showpiece Landing Page
├── PAPER/
│   ├── MANUSCRIPT_PHA_SALVAGE_BRIDGE.md           # Full companion academic manuscript (Preprint #2)
│   └── arxiv_submission/                          # Ready-to-upload arXiv LaTeX bundle & compiled PDF
│       ├── main.tex
│       ├── main.pdf
│       ├── main.bbl
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
│       ├── server.py                              # Standalone HTTP Server & REST API (Port 8790)
│       └── static/
│           └── landing.html                       # Interactive 3D Showpiece Landing Page & Scenario Explorer
└── tests/
    └── test_pha_salvage_bridge.py                 # 5-test verification suite
```
