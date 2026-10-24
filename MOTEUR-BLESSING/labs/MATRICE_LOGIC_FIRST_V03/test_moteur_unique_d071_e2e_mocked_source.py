"""D071: actual one-command orchestration using 355 synthetic source-shaped cards.

The loader is injected because the real R8 repository is PRIVATE and GitHub's
private hosted jobs have not been allocated a runner. This verifies executable
Python orchestration, NOT original private-source runtime or sports calibration.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import moteur_unique_v1 as engine
import source_graph_v04
from test_source_mechanism_dossiers_v11 import source
from test_registry import sample

CASE = {
    "fixture_id":"D071_SYNTHETIC_FULL_355_PIPELINE",
    "analysis_asof_utc":"2026-10-22T12:00:00Z",
    "kickoff_utc":"2026-10-23T19:00:00Z",
    "facts":{}
}
RATES = {
    "source_kind":"SYNTHETIC_ASSUMPTION_ONLY",
    "declared_at_utc":"2026-10-22T11:00:00Z",
    "lambda_A":1.1,"lambda_B":0.9
}

class TestD071SyntheticFullOrchestration(unittest.TestCase):
    def run_pipeline(self,modify=None):
        temp,semantic,original=source()
        if modify is not None:modify(semantic,original)
        root=Path(temp.name)
        try:
            # Inject ONLY unavailable canonical source I/O. Real graph, stage,
            # dossier, evidence, IC, 1000-grid, and manifest code is executed.
            with patch.object(engine.registry_builder,"read_canonical",return_value=sample()), \
                 patch.object(engine.enrich_registry_v03,"enrich",return_value=semantic), \
                 patch.object(engine.source_graph_v04,"extract_original_archives",return_value={}), \
                 patch.object(engine.source_graph_v04,"complete_archives",return_value=semantic), \
                 patch.object(engine.source_field_audit_v05,"original_lookup",return_value=original):
                result=engine.build(root,CASE,RATES,None,True)
            hashes=engine.persist(result,root/"output_d071")
            return result,hashes,root
        finally:
            # Return objects created in memory; no temporary files survive.
            temp.cleanup()

    def test_entire_355_real_python_path_and_1000_hypothetical_ics(self):
        result,hashes,_=self.run_pipeline()
        summary=result["summary"]
        self.assertEqual(summary["native_operational_dossiers"],355)
        self.assertEqual(summary["authentic_R8_worlds"],62)
        self.assertEqual(summary["hypothetical_sensitivity_cases"],1000)
        self.assertEqual(summary["two_team_prematch_evidence_slots"],710)
        self.assertEqual(len(result["source_graph"]["nodes"]),355)
        self.assertEqual(len(result["conceptual_stages"]["all_children"]),355)
        self.assertEqual(len(result["dossiers"]["dossiers"]),355)
        self.assertAlmostEqual(summary["theoretical_poisson_ic_pct"],59.39941502901619)
        self.assertIsNone(summary["numeric_probability_calibrated"])
        self.assertIsNone(summary["real_world_predictive_accuracy"])
        self.assertEqual(summary["remaining_324_without_individually_signed_goal_effects"],324)
        self.assertIn("R8_NATIVE_OPERATIONAL_355_PRIVATE.json",hashes)
        self.assertIn("IC_THEORETICAL_GRID_1000.json",hashes)
        self.assertTrue(result["summary"]["hypotheses_not_empirical_validation"])

    def test_archival_qualitative_state_does_not_become_goal_weight(self):
        def edit(_semantic,original):
            x=next(iter(original.values()))
            x.pop("anti_double_count_owner")
            x["scenario_tree"]["branches"]=[{
                "state_id":"SOURCE_PIT_NOT_ATTESTED",
                "label":"An archival hypothesis, not measured",
                "probability":None,"weight_source":"UNESTIMATED"}]
            x["anticipations_by_horizon"]=[
                {"horizon":z["horizon"],"method":"No future data",
                 "if_unavailable":"UNKNOWN"} for z in x["anticipations_by_horizon"]]
        result,_,_=self.run_pipeline(edit)
        row=result["dossiers"]["dossiers"][0]
        self.assertFalse(row["conditional_source_scenarios"][0]["guard_executable"])
        self.assertTrue(row["conditional_source_scenarios"][0]["guard_not_authored_abstain"])
        self.assertEqual(result["dossiers"]["source_owner_not_declared_child_count"],1)
        self.assertIsNone(row["numeric_goals_coefficient"])
        self.assertIsNone(result["summary"]["numeric_probability_calibrated"])

    def test_loss_of_one_original_child_rejected(self):
        temp,semantic,original=source()
        root=Path(temp.name)
        try:
            original.pop(next(iter(original)))
            with patch.object(engine.registry_builder,"read_canonical",return_value=sample()), \
                 patch.object(engine.enrich_registry_v03,"enrich",return_value=semantic), \
                 patch.object(engine.source_graph_v04,"extract_original_archives",return_value={}), \
                 patch.object(engine.source_graph_v04,"complete_archives",return_value=semantic), \
                 patch.object(engine.source_field_audit_v05,"original_lookup",return_value=original):
                with self.assertRaisesRegex(Exception,"REQUIRED_(EXACT_|R8_)355"):
                    engine.build(root,CASE,RATES,None,True)
        finally:temp.cleanup()

if __name__=="__main__":unittest.main()
