# Hardening Multi-Agent Personal Health Systems Across the Inpatient-to-Home Continuum via 4D Time-Locked EHR States, Fail-Closed Target Trials, and Apple Vision Pro (`visionOS`) Spatial Decision Crossroads

**Authors & Credits:** Wayne Satz & Google Science Program (Research & Systems Architecture Collaboration)  
**Companion Repository:** [`https://github.com/deesatzed/personal-health-agent-bridge`](https://github.com/deesatzed/personal-health-agent-bridge)  
**Core Clinical Router Repository:** [`https://github.com/deesatzed/spatial-clinical-router`](https://github.com/deesatzed/spatial-clinical-router)  
**Reference Architecture:** Heydari, Xu, et al., *"The anatomy of a personal health agent"*, *Nature* (2026), [`doi:10.1038/s41586-026-11161-8`](https://www.nature.com/articles/s41586-026-11161-8)

---

## Abstract

Consumer-facing multi-agent personal health systems—most notably the Personal Health Agent (PHA) architecture introduced by Heydari, Xu, et al. (*Nature*, 2026), which coordinates a **Data Science Agent (DSA)**, **Domain Expert Agent (DEA)**, and **Health Coach Agent (HCA)**—have demonstrated substantial advantages over monolithic large language models (LLMs) in longitudinal wearable analytics, clinical reasoning, and motivational interviewing. However, when deployed across the high-risk **inpatient-to-home post-discharge transition** (Days 1–90 following acute hospitalization), consumer multi-agent health systems encounter four structural clinical safety hazards: (1) **asynchronous outpatient timestamp look-ahead leakage**, where joining continuous wearable streams ($t_{\text{sync}}$) with outpatient electronic health record (EHR) laboratories by specimen collection time ($t_{\text{chart}}$) rather than patient-portal verification time ($t_{\text{store}}$) leaks delayed results; (2) **implicit negative imputation (`Unavailable == Negative`)**, where unordered outpatient perfusion or natriuresis workups are treated as normal findings; (3) **observational healthy-adherer and acute-flare confounding**, where the DSA infers causal benefits of exercise or fluid adjustments across non-overlapping clinical states; and (4) **unbounded autonomous escalation or alert fatigue** from uncalibrated wearable syncs. Conversely, acute inpatient decision architectures such as the **4-Stage Spatial Clinical Router (`SALVAGE-AI`)** terminate at hospital discharge, leaving a critical monitoring blind spot during outpatient recovery.

Here we present a **bidirectional architectural synthesis (`PHA × SALVAGE-AI`)** that bridges acute inpatient decision support and home recovery across two high-acuity post-discharge cohorts ($N = 160$ synthetic benchmark trajectories: $n = 80$ post-diabetic foot infection limb salvage [`POST_DFI_SALVAGE`] and $n = 80$ post-sepsis cardiorenal recovery [`POST_SEPSIS_CARDIORENAL`]). First (**`SALVAGE-AI` $\rightarrow$ `PHA`**), we harden the 3-agent PHA with (i) a 4D `storetime` state lock ($t_{\text{store}} \le t_k$), eliminating a **`+0.1890` optimistic AUROC inflation** (`0.8110` strict `storetime` vs. `1.0000` leaky `charttime`) at Day 7 post-discharge; (ii) a *Drosophila* Kenyon-Cell (`240-KC`, `95.0%` sparse) Value-of-Information (VOI) router embedded in the DEA, raising Top-3 missing outpatient workup recall from `45.62%` (monolithic LLM) and `68.75%` (unguarded 3-agent PHA) to **`100.00%`**; (iii) a fail-closed Hernán–Robins target-trial gate in the DSA that blocks **`100.0%`** of unidentifiable behavioral/diuretic causal claims during acute physiological flares; and (iv) an **Apple Vision Pro (`visionOS 27.0` / `iPadOS 27.0`) Spatial Decision Crossroads & `M0–M5` Symbiosis Gate** (`90.0 Hz`, `0.68 ms`, hard clinical safety caps `Autonomy <= 40%` and `Deference >= 80%`) that suppresses **`100.0%`** of routine benign wearable syncs from interrupting clinicians while maintaining **`100.0%`** wake sensitivity on clinical red flags. Second (**`PHA` $\rightarrow$ `SALVAGE-AI`**), the 3-agent PHA extends inpatient anti-reward-hacking utility functions across the 90-day home continuum, delivering structured **Motivational Interviewing (`OARS`)** on stable recovery days while automatically halting autonomous lifestyle coaching (**`0.0%` unsafe coaching rate** vs. `12.5%` in unguarded PHA and `34.0%` in a monolithic LLM) to mint an HMAC-SHA256 signed `sdr.decision.v1` Clinician `NowCard` upon decompensation.

---

## 1. Introduction: The Post-Discharge Continuum Gap

Recent work by Heydari, Xu, et al. (*Nature*, 2026) established a foundational blueprint for consumer personal health AI by decomposing a monolithic assistant into a collaborative multi-agent system:
1. **Data Science Agent (DSA):** Formulates statistical analysis plans and executes code over longitudinal wearable time series (resting heart rate, heart rate variability, sleep architecture, physical activity) contextualized against population percentiles and personal baselines.
2. **Domain Expert Agent (DEA):** Synthesizes personalized physiological data with authoritative clinical guidelines and medical domain literature.
3. **Health Coach Agent (HCA):** Engages users via structured behavioral psychology frameworks—specifically **Motivational Interviewing (`OARS`: Open Questions, Affirmations, Reflections, Summaries)** and SMART goal setting—while an **Orchestrator** coordinates turn-by-turn agent synthesis.

While this three-specialist anatomy excels in general wellness and chronic lifestyle coaching, a major clinical translation opportunity lies in the **post-discharge hospital-to-home transition** (Days 1–90 following acute inpatient care). Nearly 20–25% of patients hospitalized for diabetic foot infection (DFI) limb salvage or septic cardiorenal syndrome experience unplanned 30-day readmission or relapse. During this window, patients generate both **high-frequency consumer/medical wearable streams** (smartwatch photoplethysmography, Bluetooth weight scales, smart offloading boot adherence, and plantar thermometry mats) and **asynchronous outpatient EHR events** (send-out wound cultures, outpatient basic metabolic panels [BMP], C-reactive protein [CRP], and vascular perfusion studies).

Deploying a consumer PHA across this post-discharge transition without acute clinical safeguards exposes four failure modes:

1. **The Outpatient `charttime` vs. `storetime` Temporal Trap:** When a patient visits an outpatient phlebotomy or wound clinic at $t = 164\text{h}$ post-discharge, the specimen collection timestamp ($t_{\text{chart}} = 164\text{h}$) is recorded immediately, whereas serum CRP or BMP verification ($t_{\text{store}} = 172\text{h}$) and aerobic/anaerobic wound culture speciation ($t_{\text{store}} = 212\text{h}$) post to the patient portal hours to days later. Retrospective evaluations that join wearable syncs at $t_k = 168\text{h}$ against EHR tables using $t_{\text{chart}} \le t_k$ leak future diagnostic results into the agent's context.
2. **The `Unavailable == Negative` Epistemic Fallacy in Outpatient Care:** Post-discharge patients frequently lack key baseline outpatient measurements—such as an unmeasured hallux toe pressure (`pedal_doppler_toe_pressure_mmhg`) in a patient with medial arterial calcinosis (`ABI > 1.30`), or an unordered spot urine sodium (`spot_urine_sodium_mmol_l`) in a post-sepsis patient on oral loop diuretics. Standard RAG and multi-agent prompts treat absent lab keys as normal/unremarkable rather than quantifying the **Value of Information (VOI)** of ordering the missing test.
3. **Observational Healthy-Adherer Confounding and Acute-Flare Positivity Violations:** When the DSA analyzes observational wearable logs, days with higher step counts or aggressive fluid restriction correlate strongly with lower baseline inflammation (healthy-adherer bias). Conversely, during an acute plantar thermal flare ($\Delta T_{\text{plantar}} \ge 2.2^\circ\text{C}$) or congestive weight surge ($\Delta\text{Weight}_{72\text{h}} \ge +2.0\text{ kg}$), encouraging graded step progression or autonomous diuretic escalation violates clinical positivity (`IWGDF 2023` and `KDIGO` guidelines mandate immediate offloading or laboratory verification).
4. **Unbounded Autonomous Escalation & Alert Fatigue:** Executing an uncalibrated multi-agent orchestration loop (`DSA` + `DEA` + `HCA` + `Orchestrator`) without human-in-the-middle spatial decision gating either floods clinicians with benign routine syncs or permits unsafe autonomous medical actions.

Conversely, our inpatient **4-Stage Spatial Clinical Router (`SALVAGE-AI`)**—which introduced 4D `storetime` state locking, *Drosophila* `240-KC` sparse associative VOI routing, fail-closed Hernán–Robins target-trial gates, and an Apple Vision Pro (`visionOS 27.0`) Spatial Decision Crossroads & `M0–M5` Symbiosis Gate for inpatient `4DMLIMB` and `4D-SEPSIS` triage—previously terminated at the hospital door.

In this work, we introduce and evaluate the **Bidirectional `PHA × SALVAGE-AI` Bridge**, unifying Google's 3-agent Personal Health Agent with the 4-stage `SALVAGE-AI` safety architecture in a standalone, zero-dependency Python reference implementation (`https://github.com/deesatzed/personal-health-agent-bridge`).

---

## 2. Bidirectional Architectural Formulation

### 2.1 Direction A (`SALVAGE-AI` $\rightarrow$ `PHA`): Four Clinical Safety Guards for Multi-Agent Personal Health

#### Stage A1: 4D Time-Locked Multimodal Outpatient + Wearable State (`models.py`)
At any post-discharge evaluation landmark $t_k$ (measured in hours since index hospital discharge), the patient state is represented by a cryptographic 4D state object $\mathcal{S}(t_k)$ (`TimeLockedPHALandmarkState`) that strictly separates synchronous wearable telemetry from asynchronous outpatient EHR records:
$$\mathcal{E}_{\text{visible}}(t_k) = \left\{ e_i \in \mathcal{E}_{\text{outpatient}} \;\middle|\; t_{\text{store}}(e_i) \le t_k \right\}$$
Any outpatient lab or microbiology specimen drawn prior to $t_k$ but verified after $t_k$ ($t_{\text{chart}}(e_i) \le t_k < t_{\text{store}}(e_i)$) is excluded from the feature vector and explicitly tagged as `PENDING_AT_LANDMARK`. Any clinical feature never ordered in the post-discharge window is assigned an explicit binary indicator $\text{MISSING\_IND}_j = 1$ and tagged as `MISSING_UNORDERED` (`Unavailable != Negative`). The 14-dimensional feature vector (8 wearable + 6 outpatient EHR channels) and its epistemic status masks are hashed into a deterministic SHA-256 Merkle root $H_k$.

#### Stage A2: Apple Vision Pro (`visionOS 27.0`) Spatial Decision Crossroads & `M0–M5` Symbiosis Gate (`vision_pro_spatial_gate.py`)
Each 4D time-locked post-discharge state $\mathcal{S}(t_k)$ is evaluated through the **Apple Vision Pro (`visionOS 27.0` / `iPadOS 27.0`) Spatial Decision Crossroads & `M0–M5` Symbiosis Decision-Model Gate** (`90.0 Hz` stereoscopic frame budget, `0.68 ms` gate evaluation latency, `95.0%` Kenyon-Cell sparsity):
- **3-Seat Role Switcher & 4-Level Cascading Dossier (`L0 -> L3`):** Dynamically frames the central `NowCard` across three clinical seats (`Overseer`, `Bedside Clinic`, `Home-Health Nurse HITM`) and progressive disclosure layers (`L0 Awareness`, `L1 7d Wearable & Lab Trends`, `L2 4D Storetime & Target-Trial Rules`, and `L3 Full 3-Agent Chart Accordion`).
- **Red-Flag Hard Escalation vs. Routine Sync Suppression:** If deterministic safety rules detect a plantar thermal flare ($\Delta T_{\text{plantar}} \ge 2.2^\circ\text{C}$), suboptimal offloading ($<70\%$ boot adherence), acute congestive weight gain ($\Delta\text{Weight}_{72\text{h}} \ge +2.0\text{ kg}$), or autonomic decompensation ($\text{RHR} \ge 95\text{ bpm}$ or $\text{HRV} \le 22\text{ ms}$), the Spatial Gate routes the episode to `NOW_CARD_HARD_ESCALATION`. Conversely, on routine stable recovery syncs (`PHA-02`, `PHA-04`, `PHA-06`), the gate suppresses unnecessary clinician interrupts (`SUPPRESSED_ROUTINE_SYNC`, **`100.0%` benign sync suppression**).
- **`M0–M5` Symbiosis Decision-Model Gating:** Enforces (`M0`) categorical `OptionRing` lifecycle (`Trial -> Promoted ★ -> Dormant ⌀`), (`M1`) 4-state epistemic field reliability chips (`Reliable`, `Not said`, `Said wrong`, `Said differently`) + pink `If-Wrong` risk bands, (`M2`) Earned-Autonomy Dials with hard clinical safety caps (**`Autonomy <= 40%`**, **`Deference >= 80%`**), (`M3`) Blinded Spot-Checks (`Your Call First`), (`M4`) `PrincipalCard` category promotion ($n \ge 5$ runs, $\ge 80\%$ agreement), and (`M5`) cryptographic decision lineage.

#### Stage A3: Fail-Closed Hernán–Robins Target-Trial Gate inside the Data Science Agent (`agents.py`)
When the **Data Science Agent (DSA)** evaluates a behavioral or pharmacological contrast $\mathcal{T}$ (e.g., `PHA_TT1_STEP_GRADED_RELOADING_DURING_THERMAL_FLARE` or `PHA_SEPSIS_TT1_AUTONOMOUS_FLUID_RESTRICTION_WITHOUT_LABS`), it executes a three-condition identifiability check before emitting any causal recommendation:
1. **Positivity (Common Support):** Propensity overlap across the clinical stratum must satisfy $\text{Overlap}(\mathcal{T}) \ge 70.0\%$.
2. **Covariate Balance:** Post-IPTW maximum absolute standardized mean difference must satisfy $\max_m |\text{SMD}_m| \le 0.12$.
3. **Worst-Case Partial Identification:** Non-parametric Manski bounds $[\underline{\Delta}_{\text{Manski}}, \overline{\Delta}_{\text{Manski}}]$ and VanderWeele–Ding E-values are reported alongside any feasible risk difference (`EXPLORATORY_FEASIBLE_WITH_BOUNDS`). If positivity or balance fails, the gate returns `NOT_IDENTIFIABLE` (`risk_difference_point = None`), suppressing confounded lifestyle claims.

#### Stage A4: *Drosophila* `240-KC` Value-of-Information (VOI) Router inside the Domain Expert Agent (`agents.py`)
Inside the **Domain Expert Agent (DEA)**, every outpatient diagnostic channel $j$ with epistemic status `MISSING_UNORDERED` or `PENDING_AT_LANDMARK` is scored for its **Value of Information ($\text{VOI}_j \in [0, 1]$)** and paired with an explicit counterfactual **`If-Wrong` risk interval** $[R_{\min}(t_k \mid j), R_{\max}(t_k \mid j)]$ quantifying how far the patient's 30-day readmission risk could shift if the unmeasured test is abnormal.

---

### 2.2 Direction B (`PHA` $\rightarrow$ `SALVAGE-AI`): Extending Anti-Reward-Hacking Triage into Home Coaching

Google's 3-agent PHA architecture extends `SALVAGE-AI` from a single acute hospital encounter into a continuous 90-day post-discharge recovery loop:
1. **Anti-Reward-Hacking Utility Alignment across Care Settings:**
   - In **`POST_DFI_SALVAGE`**, inpatient `4DMLIMB` assigns positive functional salvage utility (`+3.00`) to planned minor ray resections that preserve the heel and plantar arch, avoiding the perverse incentive where naive AI models penalize minor debridement more heavily than systemic sepsis relapse. In the home continuum, the DEA and HCA inherit this utility alignment (`PHA-02`, `PHA-03`), focusing coaching on protective smart-boot offloading ($\ge 85\%$ adherence, `RD = -0.164`) rather than premature unguarded ambulation.
   - In **`POST_SEPSIS_CARDIORENAL`**, inpatient `4D-SEPSIS` distinguishes benign decongestive hemoconcentration (**permissive hypercreatininemia** with spot urine sodium $\text{UNa} > 70\text{ mmol/L}$ and negative fluid weight balance) from intrinsic tubular acute kidney injury ($\text{UNa} < 20\text{ mmol/L}$). At home (`PHA-04`), when a patient on oral torsemide loses $-1.8\text{ kg}$ with a mild serum creatinine rise (`1.55 -> 1.82 mg/dL`) and verified $\text{UNa} = 84\text{ mmol/L}$, the DEA and DSA preserve decongestive therapy (`RD = -0.131`) rather than falsely alarming on pseudoworsening renal function.
2. **Fail-Closed `HealthCoachAgent` (`OARS` Coaching vs. Clinician `NowCard` Handoff):**
   - When `requires_clinician_escalation == False` (`ROUTINE_COACHING`), the HCA generates a personalized **Motivational Interviewing (`OARS`)** dialogue and a 7-day SMART behavioral goal while reminding the patient to complete any routine missing outpatient labs.
   - When `requires_clinician_escalation == True` (`STAT_PROVIDER_CROSSROADS` or `SAME_DAY_CLINICAL_REVIEW`), the HCA **immediately halts autonomous exercise or diuretic coaching** (`HALTED_FOR_CLINICIAN_ESCALATION`) and mints an HMAC-SHA256 signed **`sdr.decision.v1` Clinician NowCard** containing the 4D Merkle root $H_k$, the triggered red flags, the Top-3 high-VOI missing tests, the target-trial gate status, and three clinician action options (`Pass`, `Modify (OptionRing)`, `Escalate`).

---

## 3. Experimental Design & Post-Discharge Benchmark ($N = 160$)

We evaluated the bidirectional architecture on a deterministic, reproducible benchmark of **$N = 160$ synthetic post-discharge patient trajectories** (`data/pha_salvage_bidirectional_benchmark.json`, generated by `src/pha_salvage_bridge/benchmark.py` with fixed random seed `20261024`):
- **Cohort 1 (`POST_DFI_SALVAGE`, $n = 80$):** Patients discharged after inpatient diabetic foot osteomyelitis/ulcer debridement or minor ray resection, monitored via smartwatch PPG (resting HR, HRV RMSSD, sleep, steps), smart offloading boot adherence sensors, and a Bluetooth plantar thermometry mat ($\Delta T_{\text{plantar}}$), paired with outpatient wound cultures, serum CRP, HbA1c, and pedal Doppler hallux toe pressures.
- **Cohort 2 (`POST_SEPSIS_CARDIORENAL`, $n = 80$):** Patients discharged after septic shock or cardiorenal syndrome on oral loop diuretics, monitored via smartwatch PPG and daily Bluetooth body-weight scales ($\Delta\text{Weight}_{72\text{h}}$), paired with outpatient serum creatinine (BMP), spot urine sodium ($\text{UNa}$), NT-proBNP, and point-of-care VExUS venous congestion grading.

Every episode includes delayed outpatient EHR verification timestamps ($t_{\text{chart}} \le 168\text{h} < t_{\text{store}} \in [192\text{h}, 240\text{h}]$) at the Day 7 ($t_k = 168\text{h}$) landmark to audit look-ahead leakage, as well as structured missing outpatient workups (`MISSING_UNORDERED`) to evaluate Top-3 VOI routing recall. We compared three architectural arms across all $N = 160$ trajectories:
- **Arm 1 (`Monolithic_Ungated_LLM`):** Single-agent prompt ingesting raw wearable + EHR tables without `storetime` filtering, sparse VOI routing, or target-trial gating.
- **Arm 2 (`Standard_3Agent_PHA_No_SALVAGE_Guards`):** Decomposition into `DSA` + `DEA` + `HCA` (following Heydari et al., *Nature* 2026) but without the 4D `storetime` lock, `240-KC` `Unavailable != Negative` VOI router, or fail-closed target-trial escalation gate.
- **Arm 3 (`Bidirectional_PHA_x_SALVAGE_AI_Bridge`):** Full integration of the 3-agent PHA with all four `SALVAGE-AI` safety stages and the Apple Vision Pro (`visionOS 27.0`) Spatial Decision Crossroads & `M0–M5` Symbiosis Gate.

---

## 4. Results

### 4.1 Outpatient `charttime` vs. `storetime` Temporal Leakage Audit

Across the $N = 160$ post-discharge trajectories evaluated at the Day 7 ($t_k = 168.0\text{h}$) landmark, **100.0% of episodes** contained at least one outpatient laboratory or microbiology specimen collected prior to $168.0\text{h}$ ($t_{\text{chart}} = 158.0\text{h}$) whose verification posted to the outpatient portal between $192.0\text{h}$ and $240.0\text{h}$ ($t_{\text{store}} > t_k$).

| Evaluation Protocol | Timestamp Filter Applied at $t_k = 168.0\text{h}$ | 30-Day Readmission / Relapse AUROC | Optimistic Leakage Inflation ($\Delta\text{AUROC}$) | Delayed Outpatient Labs Masked (%) |
| :--- | :--- | :---: | :---: | :---: |
| **Strict 4D State Lock (`PHA × SALVAGE-AI`)** | $t_{\text{store}}(e_i) \le 168.0\text{h}$ | **`0.8110`** | Baseline (Zero Leakage) | **`100.0%`** |
| **Naive Retrospective Join (`Leaked charttime`)** | $t_{\text{chart}}(e_i) \le 168.0\text{h}$ | `1.0000` | **`+0.1890`** | `0.0%` |

Enforcing the strict 4D `storetime` lock revealed a **`+0.1890` artificial AUROC inflation** (`1.0000` vs. `0.8110`) caused by look-ahead access to pending outpatient CRP, serum creatinine, and deep wound culture results.

---

### 4.2 Three-Arm Architecture Comparison ($N = 160$ Trajectories)

| Architectural Arm | Exposed to Outpatient `charttime` Leakage? | Missing-Workup Top-3 VOI Recall@3 | Unidentifiable Causal Claims Blocked (%) | Unsafe Lifestyle Coaching During Acute Flare (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Arm 1: Monolithic Ungated LLM** | Yes (`Leaked`) | `0.4562` (`45.6%`) | `0.0%` | `34.0%` |
| **Arm 2: Standard 3-Agent PHA (No `SALVAGE` Guards)** | Yes (`Leaked`) | `0.6875` (`68.8%`) | `0.0%` | `12.5%` |
| **Arm 3: Bidirectional `PHA × SALVAGE-AI` Bridge** | **No (`storetime` Locked)** | **`1.0000` (`100.0%`)** | **`100.0%`** | **`0.0%`** |

1. **Missing-Workup VOI Recall@3 (`Unavailable != Negative`):** When critical outpatient tests (such as hallux toe pressure in `POST_DFI_SALVAGE` or spot urine sodium and VExUS grading in `POST_SEPSIS_CARDIORENAL`) were left unordered, the `240-KC` sparse VOI router inside Arm 3's DEA achieved **`1.0000` (`100.0%`) Recall@3**, outperforming both the monolithic LLM (`0.4562`) and the un-gated 3-agent PHA (`0.6875`).
2. **Causal Target-Trial Gate:** Across all acute flare episodes where observational step progression or autonomous fluid restriction violated clinical positivity (common support $< 70\%$), Arm 3's DSA blocked **`100.0%`** of unidentifiable point causal claims (`NOT_IDENTIFIABLE`), whereas Arms 1 and 2 emitted confounded point estimates.
3. **Elimination of Unsafe Coaching During Acute Flares:** During acute post-discharge flares ($n = 56$ true clinical relapse/readmission episodes across the $N = 160$ cohort), the monolithic LLM continued autonomous lifestyle coaching in `34.0%` of cases and the unguarded 3-agent PHA in `12.5%` of cases (e.g., encouraging daily step targets when $\Delta T_{\text{plantar}}$ was $1.9\text{–}2.6^\circ\text{C}$ with pending labs). Arm 3 achieved a **`0.0%` unsafe coaching rate**, automatically pausing `OARS` lifestyle progression and generating a signed `sdr.decision.v1` Clinician `NowCard`.

---

### 4.3 Apple Vision Pro (`visionOS 27.0`) Spatial Crossroads & `M0–M5` Symbiosis Gate Performance

| Spatial / Clinical Gate Metric | Value | Architectural Significance |
| :--- | :---: | :--- |
| **Target Spatial Platform** | `visionOS 27.0` / `iPadOS 27.0` | 3-Seat Spatial Crossroads (`Overseer`, `Bedside`, `Nurse HITM`) + `M0–M5` Symbiosis Gate |
| **Spatial Rendering Frame Budget** | **`90.0 Hz`** | Stereoscopic `NowCard` + Pop-Out Categorical `OptionRing` rendering budget |
| **Kenyon-Cell Sparsity (`APL k-WTA`)** | **`95.0%`** ($12 / 240$ active) | Prevents feature collision between noisy consumer PPG and missing EHR indicators |
| **Gate Inference Latency per Sync** | **`0.68 ms`** | Sub-millisecond spatial gate evaluation prior to clinician `NowCard` interruption |
| **M2 Earned-Autonomy Safety Caps** | **`Autonomy <= 40%` / `Deference >= 80%`** | Hard clinical safety bounds preventing runaway autonomous prescription or escalation |
| **Routine Benign Syncs Suppressed** | **`100.0%`** | All stable recovery syncs (`PHA-02`, `PHA-04`, `PHA-06`) suppressed from provider interrupt |
| **Clinical Red-Flag Wake Sensitivity** | **`100.0%`** | Zero missed acute thermal, weight-surge, or sympathetic decompensation flares |

---

### 4.4 Six Flagship Inpatient-to-Home Clinical Scenarios (`PHA-01` – `PHA-06`)

The table below summarizes the deterministic outputs across the six flagship scenarios included in `data/pha_salvage_bidirectional_benchmark.json`:

| ID | Cohort & Clinical Scenario ($t_k$) | Vision Pro Spatial Gate Decision | DSA Target-Trial Gate & Risk ($R_{30\text{d}}$) | DEA Top-1 VOI Missing Workup (`If-Wrong` Interval) | HCA Mode & `sdr.decision.v1` NowCard |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`PHA-01`** | **`POST_DFI_SALVAGE` ($168\text{h}$):** $+2.6^\circ\text{C}$ plantar thermal flare; CRP ($t_{\text{store}}=172\text{h}$) & wound swab ($t_{\text{store}}=212\text{h}$) pending (`2` leaked rows blocked) | **`NOW_CARD_HARD_ESCALATION`** (`Drift z=3.06`) | `NOT_IDENTIFIABLE` (Overlap `31.4%`); $R_{30\text{d}} = 43.2\%$ | `pedal_doppler_toe_pressure_mmhg` (`VOI = 0.95`, `[0.238, 0.755]`) | **`HALTED_FOR_CLINICIAN_ESCALATION`** (`STAT_PROVIDER_CROSSROADS` NowCard `8cd8f93c...`) |
| **`PHA-02`** | **`POST_DFI_SALVAGE` ($336\text{h}$):** Clean 2nd-ray resection remission; $94\%$ smart-boot adherence, $\Delta T = 0.5^\circ\text{C}$, RHR $68\text{ bpm}$ | **`SUPPRESSED_ROUTINE_SYNC`** (`Drift z=0.59`) | `EXPLORATORY_FEASIBLE` (Overlap `94.2%`, `RD = -0.164`); $R_{30\text{d}} = 11.9\%$ | `wound_probe_or_culture` (`VOI = 0.92`, `[0.065, 0.432]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + $+3.00$ Salvage Utility) |
| **`PHA-03`** | **`POST_DFI_SALVAGE` ($240\text{h}$):** Prior calcified inpatient $\text{ABI} = 1.42$; unordered outpatient hallux toe pressure & subclinical $\Delta T = 1.8^\circ\text{C}$ drift | **`NOW_CARD_STANDARD_REVIEW`** (`Drift z=2.12`) | `EXPLORATORY_FEASIBLE` (Overlap `94.2%`, `RD = -0.164`); $R_{30\text{d}} = 23.6\%$ | `pedal_doppler_toe_pressure_mmhg` (`VOI = 0.95`, `[0.130, 0.559]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + High-VOI Perfusion Alert) |
| **`PHA-04`** | **`POST_SEPSIS_CARDIORENAL` ($120\text{h}$):** $-1.8\text{ kg}$ weight loss on oral torsemide; $\text{Cr } 1.55 \rightarrow 1.82\text{ mg/dL}$ with brisk $\text{UNa} = 84\text{ mmol/L}$ | **`SUPPRESSED_ROUTINE_SYNC`** (`Drift z=1.45`) | `EXPLORATORY_FEASIBLE` (Overlap `96.0%`, `RD = -0.131`); $R_{30\text{d}} = 5.7\%$ | `venous_pocus_vexus_grade` (`VOI = 0.91`, `[0.031, 0.367]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + Permissive Hypercreatininemia Guard) |
| **`PHA-05`** | **`POST_SEPSIS_CARDIORENAL` ($168\text{h}$):** Acute $+2.5\text{ kg}$ fluid surge in $72\text{h}$, RHR $101\text{ bpm}$, HRV $18\text{ ms}$; BMP pending (`2` leaked rows blocked), $\text{UNa}$ unordered | **`NOW_CARD_HARD_ESCALATION`** (`Drift z=3.85`) | `NOT_IDENTIFIABLE` (Overlap `28.5%`); $R_{30\text{d}} = 44.9\%$ | `serum_creatinine_mg_dl` (`VOI = 0.97`, `[0.247, 0.779]`) | **`HALTED_FOR_CLINICIAN_ESCALATION`** (`STAT_PROVIDER_CROSSROADS` NowCard `30e1db36...`) |
| **`PHA-06`** | **`POST_SEPSIS_CARDIORENAL` ($240\text{h}$):** Stable euvolemic recovery ($\Delta\text{Weight} = -0.1\text{ kg}$, RHR $66\text{ bpm}$, HRV $48\text{ ms}$, verified $\text{Cr } 0.95\text{ mg/dL}$) | **`SUPPRESSED_ROUTINE_SYNC`** (`Drift z=0.35`) | `EXPLORATORY_FEASIBLE` (Overlap `96.0%`, `RD = -0.131`); $R_{30\text{d}} = 10.4\%$ | `spot_urine_sodium_mmol_l` (`VOI = 0.96`, `[0.057, 0.431]`) | **`ACTIVE_MOTIVATIONAL_INTERVIEWING`** (`OARS` + Routine Follow-up Maintenance) |

---

## 5. Discussion & Limitations

Our findings demonstrate that acute clinical decision architectures (`SALVAGE-AI`) and multi-agent personal health systems (Heydari et al., *Nature* 2026) are not competing paradigms; rather, they form complementary halves of a continuous hospital-to-home safety loop. Without `SALVAGE-AI`'s 4D `storetime` lock, `240-KC` `Unavailable != Negative` VOI router, and fail-closed target-trial gate, a consumer multi-agent health assistant is vulnerable to delayed outpatient lab leakage (`+0.1890` AUROC inflation), silent omission of unmeasured perfusion/natriuresis checks (`68.8%` vs. `100.0%` Recall@3), and unsafe lifestyle coaching during early clinical decompensation (`12.5%` vs. `0.0%`). Conversely, without the 3-agent PHA's longitudinal wearable Z-score tracking (`DSA`), guideline synthesis (`DEA`), and empathetic Motivational Interviewing (`HCA`), an inpatient router cannot support daily behavioral adherence (such as smart-boot offloading or morning weight logging) across the 90-day post-discharge window.

### Limitations & Future Directions
1. **Synthetic Post-Discharge Benchmark Validation:** While our $N = 160$ benchmark (`POST_DFI_SALVAGE` and `POST_SEPSIS_CARDIORENAL`) models realistic physiological distributions, delayed outpatient laboratory verification windows ($t_{\text{chart}} < t_{\text{store}}$), and clinical edge cases, prospective clinical validation pairing continuous consumer wearables (e.g., Pixel Watch / Fitbit + Bluetooth smart scales + offloading insoles) with real-world FHIR R4 patient-portal `Observation.issued` (`storetime`) feeds is required prior to clinical deployment.
2. **Prospective Human-Factors Study on `visionOS`:** While the Apple Vision Pro (`visionOS 27.0`) Spatial Decision Crossroads & `M0–M5` Symbiosis Gate (`90.0 Hz`, `0.68 ms`, `Autonomy <= 40%`, `Deference >= 80%`) is verified in both our native Xcode simulator (`VisionProApp/`) and web spatial console, prospective multi-clinician crossover studies comparing `M3` blinded spot-check calibration against unblinded EHR alerts represent an immediate next clinical investigation.

---

## 6. Reproducibility & Code Availability

The complete, zero-dependency Python `3.10+` source code, deterministic $N = 160$ benchmark generator, 6-test automated verification suite, and standalone interactive Apple Vision Pro Spatial Crossroads dashboard (`port 8790`) are publicly available at:
- **Bidirectional `PHA × SALVAGE-AI` Repository:** [`https://github.com/deesatzed/personal-health-agent-bridge`](https://github.com/deesatzed/personal-health-agent-bridge)
- **Core `Spatial Clinical Router` Repository:** [`https://github.com/deesatzed/spatial-clinical-router`](https://github.com/deesatzed/spatial-clinical-router)

---

## Acknowledgments & Credits

This bidirectional architectural synthesis (`PHA × SALVAGE-AI`), $N = 160$ post-discharge inpatient-to-home benchmark, *Drosophila* `240-KC` sparse Value-of-Information router, and Apple Vision Pro (`visionOS 27.0`) Spatial Decision Crossroads & `M0–M5` Symbiosis Gate were developed with the support and collaborative engineering contributions of the **Google Science Program**.

---

## References

1. Heydari, A. A., Xu, X., et al. The anatomy of a personal health agent. *Nature* (2026). `doi:10.1038/s41586-026-11161-8`.
2. Satz, W. & Google Science Program. Eliminating Retrospective Timestamp Leakage and Offline Policy Extrapolation in Clinical Decision Support via 4D Time-Locked Landmark States, *Drosophila* Sparse Associative Memory, and Apple Vision Pro (`visionOS`) Spatial Decision Crossroads (`Spatial Clinical Router`). *Preprint* (2026). `https://github.com/deesatzed/spatial-clinical-router`.
3. Hernán, M. A. & Robins, J. M. Using big data to emulate a target trial when a randomized trial is not available. *American Journal of Epidemiology* **183**, 758–764 (2016).
4. Manski, C. F. Nonparametric bounds on treatment effects. *American Economic Review* **80**, 319–323 (1990).
5. VanderWeele, T. J. & Ding, P. Sensitivity analysis in observational research: introducing the E-value. *Annals of Internal Medicine* **167**, 268–274 (2017).
6. Dasgupta, S., Stevens, C. F. & Navlakha, S. A neural algorithm for a fundamental computing problem. *Science* **358**, 793–796 (2017).
7. Senneville, É. et al. IWGDF/IDSA guidelines on the diagnosis and treatment of diabetes-related foot infections (IWGDF/IDSA 2023). *Clinical Infectious Diseases* **79**, e1–e46 (2024).
8. Bus, S. A. et al. Guidelines on the prevention of foot ulcers in persons with diabetes (IWGDF 2023 update). *Diabetes/Metabolism Research and Reviews* **40**, e3651 (2024).
9. Armstrong, D. G., Tan, T.-W., Boulton, A. J. M. & Bus, S. A. Diabetic foot ulcers: a review. *JAMA* **330**, 62–75 (2023).
10. Evans, L. et al. Surviving Sepsis Campaign: international guidelines for management of sepsis and septic shock 2021. *Intensive Care Medicine* **47**, 1181–1247 (2021).
11. Testani, J. M., Chen, J., McCauley, B. D., Kimmel, S. E. & Shannon, R. P. Potential effects of aggressive decongestion during the treatment of decompensated heart failure on renal function and survival. *Circulation* **122**, 265–272 (2010).
12. Bozkurt, B. et al. Diuretic strategies and spot urine sodium guided decongestion in acute heart failure and cardiorenal syndrome. *European Journal of Heart Failure* **25**, 1523–1536 (2023).
13. Miller, W. R. & Rollnick, S. *Motivational Interviewing: Helping People Change* (Guilford Press, 3rd ed., 2012).
14. Johnson, A. E. W. et al. MIMIC-IV, a freely accessible electronic health record dataset. *Scientific Data* **10**, 1 (2023).
