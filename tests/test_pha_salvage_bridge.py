"""
Automated Unit & Integration Test Suite for the Standalone `PHA × SALVAGE-AI` Bridge (`test_pha_salvage_bridge.py`).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pha_salvage_bridge.agents import PersonalHealthOrchestrator
from pha_salvage_bridge.benchmark import (
    build_flagship_pha_scenarios,
    run_bidirectional_pha_benchmark,
)
from pha_salvage_bridge.models import build_time_locked_pha_state


class TestPHASalvageBridge(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = PersonalHealthOrchestrator()
        self.scenarios = {s["scenario_id"]: s for s in build_flagship_pha_scenarios()}

    def test_direction_a1_outpatient_storetime_lock_blocks_future_labs(self) -> None:
        """Verify strict `storetime <= t_k` masks pending outpatient CRP & wound culture at Day 7 (PHA-01)."""
        sc = self.scenarios["PHA-01"]
        strict_state = build_time_locked_pha_state(
            sc["scenario_id"],
            sc["patient_id"],
            sc["cohort_domain"],
            sc["t_landmark_hours"],
            sc["wearable_stream"],
            sc["ehr_records"],
            strict_storetime_lock=True,
        )
        naive_state = build_time_locked_pha_state(
            sc["scenario_id"],
            sc["patient_id"],
            sc["cohort_domain"],
            sc["t_landmark_hours"],
            sc["wearable_stream"],
            sc["ehr_records"],
            strict_storetime_lock=False,
        )
        self.assertEqual(len(strict_state.admitted_ehr_records), 0)
        self.assertEqual(len(strict_state.pending_ehr_records), 2)
        self.assertEqual(len(naive_state.admitted_ehr_records), 2)
        self.assertNotEqual(strict_state.merkle_root, naive_state.merkle_root)

    def test_direction_a2_240kc_voi_router_unavailable_not_negative(self) -> None:
        """Verify Domain Expert Agent ranks unmeasured hallux toe pressure #1 VOI in PHA-03 (`Unavailable != Negative`)."""
        sc = self.scenarios["PHA-03"]
        state = build_time_locked_pha_state(
            sc["scenario_id"],
            sc["patient_id"],
            sc["cohort_domain"],
            sc["t_landmark_hours"],
            sc["wearable_stream"],
            sc["ehr_records"],
            strict_storetime_lock=True,
        )
        resp = self.orchestrator.run_episode_landmark(state)
        top_voi = resp.dea_output.top_voi_missing_workup
        self.assertGreaterEqual(len(top_voi), 2)
        self.assertEqual(top_voi[0].feature_key, "pedal_doppler_toe_pressure_mmhg")
        self.assertGreaterEqual(top_voi[0].voi_score, 0.90)

    def test_direction_a3_fail_closed_target_trial_and_anti_reward_hacking(self) -> None:
        """Verify fail-closed positivity gate on thermal/congestive flares (PHA-01, PHA-05) and permissive Cr reward alignment (PHA-04)."""
        # PHA-01: Plantar thermal flare >= 2.2 C -> NOT_IDENTIFIABLE for step progression
        sc1 = self.scenarios["PHA-01"]
        st1 = build_time_locked_pha_state(
            sc1["scenario_id"], sc1["patient_id"], sc1["cohort_domain"], sc1["t_landmark_hours"], sc1["wearable_stream"], sc1["ehr_records"]
        )
        r1 = self.orchestrator.run_episode_landmark(st1)
        self.assertEqual(r1.dsa_output.target_trial_contrast.gate_status, "NOT_IDENTIFIABLE")
        self.assertIsNone(r1.dsa_output.target_trial_contrast.risk_difference_point)

        # PHA-04: Permissive hypercreatininemia with Spot Urine Na 84 mmol/L -> EXPLORATORY_FEASIBLE_WITH_BOUNDS
        sc4 = self.scenarios["PHA-04"]
        st4 = build_time_locked_pha_state(
            sc4["scenario_id"], sc4["patient_id"], sc4["cohort_domain"], sc4["t_landmark_hours"], sc4["wearable_stream"], sc4["ehr_records"]
        )
        r4 = self.orchestrator.run_episode_landmark(st4)
        self.assertEqual(r4.dsa_output.target_trial_contrast.gate_status, "EXPLORATORY_FEASIBLE_WITH_BOUNDS")
        self.assertLess(r4.dsa_output.target_trial_contrast.risk_difference_point, 0.0)
        self.assertIn("permissive hypercreatininemia", r4.dea_output.reward_alignment_note)

    def test_direction_a4_and_b_vision_pro_spatial_gate_and_hca_escalation_bridge(self) -> None:
        """Verify Vision Pro Spatial Gate suppresses interrupts on stable days (PHA-02, PHA-06) and HCA mints `sdr.decision.v1` NowCard on flares (PHA-01, PHA-05)."""
        # Stable day (PHA-06) -> Routine sync suppressed at Spatial Gate, active motivational interviewing
        sc6 = self.scenarios["PHA-06"]
        st6 = build_time_locked_pha_state(
            sc6["scenario_id"], sc6["patient_id"], sc6["cohort_domain"], sc6["t_landmark_hours"], sc6["wearable_stream"], sc6["ehr_records"]
        )
        r6 = self.orchestrator.run_episode_landmark(st6)
        self.assertFalse(r6.vision_pro_gate.wake_cloud_orchestrator)
        self.assertTrue(r6.vision_pro_gate.suppress_cloud_wakeup)
        self.assertEqual(r6.vision_pro_gate.spatial_crossroads_mode, "SUPPRESSED_ROUTINE_SYNC")
        self.assertEqual(r6.vision_pro_gate.kc_sparsity_pct, 95.0)
        self.assertEqual(r6.hca_output.coaching_mode, "ACTIVE_MOTIVATIONAL_INTERVIEWING")
        self.assertIsNone(r6.hca_output.clinician_nowcard_handoff)

        # Acute congestive weight surge (PHA-05) -> Vision Pro Spatial Gate triggers NOW_CARD_HARD_ESCALATION, HCA halts coaching & mints signed NowCard
        sc5 = self.scenarios["PHA-05"]
        st5 = build_time_locked_pha_state(
            sc5["scenario_id"], sc5["patient_id"], sc5["cohort_domain"], sc5["t_landmark_hours"], sc5["wearable_stream"], sc5["ehr_records"]
        )
        r5 = self.orchestrator.run_episode_landmark(st5)
        self.assertTrue(r5.vision_pro_gate.wake_cloud_orchestrator)
        self.assertEqual(r5.vision_pro_gate.spatial_crossroads_mode, "NOW_CARD_HARD_ESCALATION")
        self.assertLessEqual(r5.vision_pro_gate.earned_autonomy_dials["autonomy_pct"], 40)
        self.assertGreaterEqual(r5.vision_pro_gate.earned_autonomy_dials["deference_pct"], 80)
        self.assertIn("overseer", r5.vision_pro_gate.role_seat_framings)
        self.assertIn("L2_storetime_target_trial", r5.vision_pro_gate.cascading_dossier)
        self.assertEqual(r5.hca_output.coaching_mode, "HALTED_FOR_CLINICIAN_ESCALATION")
        self.assertIsNotNone(r5.hca_output.clinician_nowcard_handoff)
        self.assertEqual(r5.hca_output.clinician_nowcard_handoff["schema"], "sdr.decision.v1")

    def test_n160_bidirectional_benchmark_metrics(self) -> None:
        """Verify N=160 benchmark quantifies outpatient lookahead leakage and 100% red-flag wake sensitivity."""
        res = run_bidirectional_pha_benchmark(seed=20261023)
        self.assertEqual(res["total_episodes_n"], 160)
        self.assertGreater(res["outpatient_timestamp_leakage_audit"]["auroc_inflation_delta"], 0.05)
        self.assertEqual(res["vision_pro_spatial_gate_audit"]["clinical_red_flag_wake_sensitivity_pct"], 100.0)
        self.assertGreater(res["vision_pro_spatial_gate_audit"]["routine_benign_syncs_suppressed_pct"], 80.0)
        self.assertEqual(
            res["three_arm_architecture_comparison"]["Arm_3_Bidirectional_PHA_x_SALVAGE_AI_Bridge"]["missing_workup_voi_recall_at_3"],
            1.0,
        )

    def test_two_tier_frontend_landing_and_live_workspace_simulation(self) -> None:
        """Verify separate `/landing` and `/workspace` HTML assets and live `/api/simulate` engine."""
        from pha_salvage_bridge.server import STATIC_LANDING_PATH, STATIC_WORKSPACE_PATH, simulate_custom_pha_state

        self.assertTrue(STATIC_LANDING_PATH.exists())
        self.assertTrue(STATIC_WORKSPACE_PATH.exists())
        self.assertNotEqual(STATIC_LANDING_PATH.read_text(encoding="utf-8"), STATIC_WORKSPACE_PATH.read_text(encoding="utf-8"))

        sim_flare = simulate_custom_pha_state(
            {
                "episode_id": "PHA-SIM-FLARE",
                "cohort_domain": "POST_DFI_SALVAGE",
                "plantar_temp_asymmetry_c": 2.7,
                "weight_delta_kg": 0.4,
                "rhr_bpm": 91.0,
                "hrv_rmssd_ms": 22.0,
                "boot_offloading_adherence_pct": 50.0,
                "strict_storetime_lock": True,
                "verified_outpatient_keys": [],
            }
        )
        self.assertTrue(sim_flare["vision_pro_gate"]["wake_cloud_orchestrator"])
        self.assertEqual(sim_flare["dsa_output"]["leakage_rows_blocked"], 3)
        self.assertEqual(sim_flare["hca_output"]["coaching_mode"], "HALTED_FOR_CLINICIAN_ESCALATION")
        self.assertIsNotNone(sim_flare["hca_output"]["clinician_nowcard_handoff"])


if __name__ == "__main__":
    unittest.main()
