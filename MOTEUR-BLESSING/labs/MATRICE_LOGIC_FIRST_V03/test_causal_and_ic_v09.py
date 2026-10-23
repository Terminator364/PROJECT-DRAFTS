"""D062 regression tests: all 355 routed + honest Poisson sensitivity model."""
from __future__ import annotations
import copy,math,unittest
from test_source_graph_v04 import data
import source_graph_v04 as src
import causal_stages_v07 as stages
import theoretical_ic_v08 as calc

def fixture():
    return {"fixture_id":"D062_EXAMPLE_ONLY",
            "analysis_asof_utc":"2026-10-22T12:00:00Z",
            "kickoff_utc":"2026-10-23T19:00:00Z"}

def assumptions():
    return {"source_kind":"SYNTHETIC_ASSUMPTION_ONLY",
            "declared_at_utc":"2026-10-22T11:00:00Z",
            "lambda_A":1.1,"lambda_B":0.9}

class TestEveryDocumentaryChild(unittest.TestCase):
    def test_all_62_worlds_partitioned_once(self):
        self.assertEqual(set(stages.STAGE_BY_WORLD),set(stages.v02.core.CANONICAL_WORLDS))
        self.assertEqual(len(stages.STAGE_BY_WORLD),62)
        self.assertEqual(set(stages.WORLD_STAGE),set(stages.STAGE_NOTES))
    def test_real_form_355_nodes_routed_without_claiming_causal_effect(self):
        temp,source=data()
        try:
            graph=src.graph(source)
            product=stages.route_source_graph(graph)
            self.assertEqual(len(product["all_children"]),355)
            self.assertEqual(sum(product["stage_counts"].values()),355)
            self.assertEqual(len(product["conceptual_process_edges"]),8)
            self.assertEqual(product["signed_per_child_goal_effects"],0)
            self.assertIsNone(product["goal_probability_law_from_355"])
            self.assertTrue(all(x["causal_effect_sign"] is None for x in product["all_children"]))
        finally:temp.cleanup()
    def test_dangling_contract_reference_preserved(self):
        temp,source=data()
        try:
            graph=src.graph(source)
            graph["unresolved_source_references"]=[{"from":"A.B","reference":"NOT_IN_REGISTRY"}]
            prod=stages.route_source_graph(graph)
            self.assertEqual(prod["unresolved_documentary_references"],graph["unresolved_source_references"])
        finally:temp.cleanup()
    def test_unapproved_effect_not_promoted(self):
        temp,source=data()
        try:
            graph=src.graph(source)
            graph["nodes"][0]["IC_effect"]=1.0
            with self.assertRaisesRegex(ValueError,"UNAUTHORIZED_GOAL_EFFECT"):
                stages.route_source_graph(graph)
        finally:temp.cleanup()

class TestTheoreticalIC(unittest.TestCase):
    def test_two_goal_probability_exact_math(self):
        out=calc.poisson_over15(1.1,0.9)
        self.assertAlmostEqual(out["IC_over15_theoretical_percent"],59.399415025901755,places=9)
        self.assertAlmostEqual(out["P_0_total_goals"]+out["P_exactly_1_goal"]+out["P_over_1_5_goals"],1.0,places=12)
        self.assertIsNone(out["reliability_or_accuracy_percent"])
    def test_monotonic_in_goal_intensity(self):
        previous=-1.0
        for i in range(0,49):
            value=calc.poisson_over15(i/10,0.9)["P_over_1_5_goals"]
            self.assertGreaterEqual(value,previous-1e-14)
            previous=value
    def test_zero_goal_rate_no_over15(self):
        self.assertAlmostEqual(calc.poisson_over15(0,0)["P_over_1_5_goals"],0)
    def test_invalid_rates_fail_closed(self):
        for wrong in (True,"1.2",-1,float("nan"),float("inf"),30):
            with self.subTest(value=str(wrong)):
                with self.assertRaises(calc.UnjustifiedIC):calc.poisson_over15(wrong,1)
    def test_absent_hypothesis_no_ic_not_zero(self):
        out=calc.evaluate(fixture())
        self.assertIsNone(out["IC_over15_theoretical_percent"])
        self.assertIsNone(out["IC_over15_calibrated_percent"])
    def test_hypothetical_ic_is_never_claimed_calibrated(self):
        out=calc.evaluate(fixture(),assumptions())
        self.assertAlmostEqual(out["IC_over15_theoretical_percent"],59.399415025901755,places=9)
        self.assertIsNone(out["IC_over15_calibrated_percent"])
        self.assertEqual(out["status"],"CONDITIONAL_LAB_IC_NOT_REAL_MATCH_RECOMMENDATION")
        self.assertFalse(out["goal_rates_inferred_from_R8_children"])
    def test_assumption_interval_is_sensitivity_not_confidence(self):
        h={**assumptions(),"lambda_A_range":[0.8,1.4],"lambda_B_range":[0.6,1.2]}
        out=calc.evaluate(fixture(),h)
        interval=out["sensitivity_range"]
        self.assertLess(interval["over15_percent_lower"],out["IC_over15_theoretical_percent"])
        self.assertGreater(interval["over15_percent_upper"],out["IC_over15_theoretical_percent"])
        self.assertIn("NOT_STATISTICAL_CONFIDENCE",interval["range_type"])
    def test_future_sources_blocked(self):
        h={**assumptions(),"declared_at_utc":"2026-10-22T14:00:00Z"}
        with self.assertRaisesRegex(calc.UnjustifiedIC,"FUTURE_HYPOTHESIS"):
            calc.evaluate(fixture(),h)
        f={**fixture(),"analysis_asof_utc":"2026-10-23T20:00:00Z"}
        with self.assertRaisesRegex(calc.UnjustifiedIC,"CUTOFF_NOT_BEFORE"):
            calc.evaluate(f,h)
        f={**fixture(),"target_match_final":True}
        with self.assertRaisesRegex(calc.UnjustifiedIC,"FUTURE_OUTCOME"):
            calc.evaluate(f,assumptions())
    def test_no_pretended_355_derived_rates(self):
        h={**assumptions(),"rates_derived_from_355_without_model":True}
        with self.assertRaisesRegex(calc.UnjustifiedIC,"NO_FABRICATED"):
            calc.evaluate(fixture(),h)
        h={**assumptions(),"claimed_empirical_validation":True}
        with self.assertRaisesRegex(calc.UnjustifiedIC,"NO_FABRICATED"):
            calc.evaluate(fixture(),h)
    def test_full_355_evidence_requirement_when_given(self):
        good={"source_children":355,"two_team_evidence_slots":710,"numeric_IC_calibrated":None}
        self.assertIsNotNone(calc.evaluate(fixture(),assumptions(),good)["IC_over15_theoretical_percent"])
        bad={**good,"source_children":354}
        with self.assertRaisesRegex(calc.UnjustifiedIC,"REQUIRE_FULL_355"):
            calc.evaluate(fixture(),assumptions(),bad)
    def test_synthetic_grid_1000_unique_monotonic_unvalidated(self):
        data=calc.synthetic_grid_1000()
        self.assertEqual(data["scenario_count"],1000)
        self.assertEqual(len(data["scenarios"]),1000)
        self.assertEqual(len({(s["lambda_A_assumed"],s["lambda_B_assumed"]) for s in data["scenarios"]}),1000)
        self.assertTrue(all(s["probability_is_calibrated"] is False for s in data["scenarios"]))
        self.assertIsNone(data["accuracy_pct"])
        self.assertIsNone(data["IC_calibrated"])

if __name__=="__main__":unittest.main()
