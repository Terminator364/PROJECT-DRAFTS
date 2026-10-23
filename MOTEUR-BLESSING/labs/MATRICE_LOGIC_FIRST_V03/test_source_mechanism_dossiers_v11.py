import copy,unittest
from test_source_graph_v04 import data
from source_graph_v04 import SourceGraphError
import source_mechanism_dossiers_v11 as md

H=("J-6","J-5","J-3","J-1","H-9","H-1")
def source():
    temp,sem=data()
    originals={}
    for row in sem["subparameters"]:
        cid=row["id"]
        originals[cid]={"id":cid,"parent_world_id":row["world"],
             "name_fr":cid.split(".")[1],
             "scoring_active":False,"numeric_effect":None,
             "anti_double_count_owner":row["world"],
             "required_inputs":["fixture_id","asof_utc","source_snapshot_id"],
             "evidence_search_plan":[{"provider":"original_publisher"}],
             "anticipations_by_horizon":[{"horizon":h,"procedure":"prematch only"} for h in H],
             "scenario_tree":{"branches":[{"id":cid+".SUPPORT",
                                          "guard":"archived before cutoff",
                                          "qualitative_consequence":"documentary eligibility only",
                                          "weight":None}]}}
    return temp,sem,originals

class TestAll355Dossiers(unittest.TestCase):
    def test_exact_source_cards_and_no_goal_weights(self):
        t,sem,orig=source()
        try:
            d=md.dossiers(sem,orig)
            self.assertEqual(d["operational_dossiers"],355)
            self.assertEqual(len(d["dossiers"]),355)
            self.assertEqual(d["prematch_slots_two_teams"],710)
            self.assertEqual(d["manual_signed_causal_effects"],0)
            self.assertIsNone(d["empirical_calibration"])
            self.assertTrue(all(len(x["prematch_six_horizons"])==6 for x in d["dossiers"]))
            self.assertTrue(all(x["numeric_goals_coefficient"] is None for x in d["dossiers"]))
        finally:t.cleanup()
    def test_missing_original_fails_closed(self):
        t,sem,orig=source()
        try:
            orig.pop(next(iter(orig)))
            with self.assertRaisesRegex(SourceGraphError,"REQUIRED_R8_355"):
                md.dossiers(sem,orig)
        finally:t.cleanup()
    def test_missing_owner_fails_closed(self):
        t,sem,orig=source()
        try:
            next(iter(orig.values())).pop("anti_double_count_owner")
            with self.assertRaisesRegex(SourceGraphError,"ANTI_DOUBLE_COUNT_OWNER"):
                md.dossiers(sem,orig)
        finally:t.cleanup()
    def test_unweighted_scenarios_only(self):
        t,sem,orig=source()
        try:
            next(iter(orig.values()))["scenario_tree"]["branches"][0]["weight"]=0.8
            with self.assertRaisesRegex(SourceGraphError,"FORBIDDEN_SOURCE_BRANCH_WEIGHTS"):
                md.dossiers(sem,orig)
        finally:t.cleanup()
    def test_absent_case_guard_stops(self):
        t,sem,orig=source()
        try:
            next(iter(orig.values()))["scenario_tree"]["branches"][0].pop("guard")
            with self.assertRaisesRegex(SourceGraphError,"UNSPECIFIED_SOURCE_BRANCH_GUARD"):
                md.dossiers(sem,orig)
        finally:t.cleanup()
    def test_source_text_not_invented(self):
        t,sem,orig=source()
        try:
            d=md.dossiers(sem,orig)
            self.assertIsNone(d["dossiers"][0]["native_source_question_or_definition"])
            self.assertEqual(d["counts"]["no_original_descriptive_sentence"],355)
        finally:t.cleanup()
if __name__=="__main__":unittest.main()
