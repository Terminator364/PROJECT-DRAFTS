import copy,unittest
import shot_process_v10 as m
from theoretical_ic_v08 import UnjustifiedIC
from test_source_graph_v04 import data
import source_graph_v04

def fixture():
    return {"fixture_id":"D063_LAB_FIXTURE",
            "analysis_asof_utc":"2026-10-22T12:00:00Z",
            "kickoff_utc":"2026-10-23T19:00:00Z"}

def proposal(p1=0.5,p2=0.5):
    return {"projection_kind":"HYPOTHETICAL_PRET0_SHOT_EVENTS",
            "projection_declared_at_utc":"2026-10-22T11:00:00Z",
            "shots_A":[{"shot_slot_id":"A1","event_type":"OPEN_PLAY","p_goal_if_projected_event":p1}],
            "shots_B":[{"shot_slot_id":"B1","event_type":"SET_PIECE","p_goal_if_projected_event":p2}]}

class TestHonestProjectedShotEngine(unittest.TestCase):
    def test_two_independent_half_chances_p_two_is_one_quarter(self):
        o=m.calculate(fixture(),proposal())
        self.assertAlmostEqual(o["IC_over15_theoretical_percent"],25.0,places=11)
        self.assertAlmostEqual(o["P_0_goals_conditional"],0.25)
        self.assertAlmostEqual(o["P_exactly_1_goal_conditional"],0.5)
        self.assertIsNone(o["IC_over15_empirically_calibrated_percent"])
    def test_single_shot_never_over15_and_empty_never_proves_real_under(self):
        a=proposal();a["shots_B"]=[]
        self.assertAlmostEqual(m.calculate(fixture(),a)["IC_over15_theoretical_percent"],0.0)
        a["shots_A"]=[]
        out=m.calculate(fixture(),a)
        self.assertEqual(out["shot_event_count_assumed"],0)
        self.assertIsNone(out["real_match_predictive_accuracy_percent"])
    def test_three_half_chances_p_more_than_one_is_half(self):
        a=proposal()
        a["shots_A"].append({"shot_slot_id":"A2","event_type":"OPEN_PLAY","p_goal_if_projected_event":0.5})
        out=m.calculate(fixture(),a)
        self.assertAlmostEqual(out["IC_over15_theoretical_percent"],50.0,places=10)
    def test_zero_or_certain_probabilities(self):
        self.assertEqual(m.calculate(fixture(),proposal(0,0))["IC_over15_theoretical_percent"],0.0)
        self.assertEqual(m.calculate(fixture(),proposal(1,1))["IC_over15_theoretical_percent"],100.0)
    def test_duplicate_event_between_teams_rejected(self):
        a=proposal();a["shots_B"][0]["shot_slot_id"]="A1"
        with self.assertRaisesRegex(UnjustifiedIC,"DUPLICATE_SHARED_SHOT"):
            m.calculate(fixture(),a)
    def test_unverified_target_match_events_rejected(self):
        a=proposal();a["shots_A"][0]["observed_in_target_match"]=True
        with self.assertRaisesRegex(UnjustifiedIC,"FUTURE_TARGET_SHOT_LEAK"):
            m.calculate(fixture(),a)
        a=proposal();a["target_match_shots_observed"]=True
        with self.assertRaisesRegex(UnjustifiedIC,"NO_INPLAY_SHOTS"):
            m.calculate(fixture(),a)
    def test_projection_must_be_declared_before_pret0(self):
        a=proposal();a["projection_declared_at_utc"]="2026-10-22T16:00:00Z"
        with self.assertRaisesRegex(UnjustifiedIC,"CREATED_AFTER_ANALYSIS"):
            m.calculate(fixture(),a)
    def test_negative_nan_string_and_bool_blocked(self):
        for invalid in (-.1,1.1,float("nan"),float("inf"),"0.5",True):
            a=proposal();a["shots_A"][0]["p_goal_if_projected_event"]=invalid
            with self.subTest(value=str(invalid)),self.assertRaises(UnjustifiedIC):
                m.calculate(fixture(),a)
    def test_conditional_model_keeps_mechanism_reference_nonweighted(self):
        t,sem=data()
        try:
            graph=source_graph_v04.graph(sem)
            name=graph["nodes"][0]["id"]
            a=proposal();a["shots_A"][0]["source_child_context_ids"]=[name]
            out=m.calculate(fixture(),a,graph)
            self.assertTrue(out["source_graph_context_verified"])
            self.assertTrue(out["teams"]["A"]["slots"][0]["source_child_context_not_a_weight"])
            self.assertFalse(out["all_R8_children_used_to_estimate_conversion_probabilities"])
        finally:t.cleanup()
    def test_noncanonical_subparameter_not_accepted(self):
        t,sem=data()
        try:
            graph=source_graph_v04.graph(sem)
            a=proposal()
            a["shots_A"][0]["source_child_context_ids"]=["FAKE_WORLD.FAKE_CHILD"]
            with self.assertRaisesRegex(UnjustifiedIC,"UNREGISTERED_SOURCE_CHILD"):
                m.calculate(fixture(),a,graph)
        finally:t.cleanup()
    def test_malformed_event_list_refused(self):
        a=proposal();a["shots_A"]=[{}]
        with self.assertRaisesRegex(UnjustifiedIC,"UNIQUE_SHOT_SLOT_REQUIRED"):
            m.calculate(fixture(),a)
    def test_assumptions_do_not_create_r8_training(self):
        o=m.calculate(fixture(),proposal(.2,.3))
        self.assertEqual(o["status"],"LAB_CONDITIONAL_SHOT_PROCESS_NOT_A_VALIDATED_MATCH_IC")
        self.assertIsNone(o["real_goal_count_observed"])
        self.assertEqual(o["model_limits"],
            "PROJECTED_EVENT_COUNT_AND_PER_EVENT_CONVERSION_ARE_SUPPLIED_HYPOTHESES_NOT_FORECASTS")

if __name__=="__main__":unittest.main()
