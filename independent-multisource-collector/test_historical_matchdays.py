"""Offline acceptance tests: one historical library, 62 family slots, J1..J6."""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from build_historical_matchdays import build

HERE=Path(__file__).resolve().parent
CUTOFF=dt.date(2026,10,17)
HIST=HERE/"05_JOURNEES"/"HISTORIQUE_J1_ACTUEL"


class HistoricalArchiveTests(unittest.TestCase):
    def test_archive_stored_and_complete(self):
        result=json.loads((HIST/"INDEX_HISTORIQUE.json").read_text(encoding="utf-8"))
        self.assertEqual(result["historical_matches"],120)
        self.assertEqual(result["l3_documented_children_in_index"],109)
        self.assertEqual(result["source_errors"],[])
        self.assertFalse(result["prediction_ic_enabled"])
        for code in ("E0","I1"):
            day_counts=result["leagues"][code]["per_matchday"]
            byday={p["matchday"]:p["completed"] for p in day_counts}
            self.assertEqual({i:byday[i] for i in range(1,7)},{i:10 for i in range(1,7)})
            self.assertEqual(result["leagues"][code]["families"],62)

    def test_split_outcome_vs_prematch(self):
        for code in ("E0","I1"):
            for day in range(1,7):
                data=json.loads((HIST/code/("J%02d"%day)/"matchday.json").read_text(encoding="utf-8"))
                self.assertEqual(data["completed_matches_in_archives"],10)
                self.assertEqual(data["missing_results_before_cutoff"],0)
                self.assertFalse(data["prematch_replay_certified"])
                for record in data["matches"]:
                    pre=record["prematch_identity_observed_in_current_archive"]
                    post=record["outcome_known_only_after_game"]
                    self.assertNotIn("FTHG",pre)
                    self.assertNotIn("FTAG",pre)
                    self.assertNotIn("over15_fulltime_training_label",pre)
                    self.assertEqual(post["over15_fulltime_training_label"],
                                     int(sum(post["full_time_goals"])>=2))
                    self.assertTrue(post["full_time_score_label_not_a_feature"])
                    self.assertFalse(record["source_and_asof"]["historical_asof_replay_certified"])
                    self.assertLess(dt.date.fromisoformat(record["source_and_asof"]["match_date"]),CUTOFF)
    def test_all_62_worlds_and_109_children(self):
        for code in ("E0","I1"):
            cov=json.loads((HIST/code/"family_62_coverage.json").read_text(encoding="utf-8"))
            self.assertEqual(cov["family_count"],62)
            self.assertEqual(len(cov["parent_families"]),62)
            self.assertEqual(cov["l3_documented_family_count"],20)
            self.assertEqual(cov["l3_documented_subparam_count"],109)
            self.assertTrue(all(not x["prematch_PIT_certified"] and not x["ic_eligible"]
                                for x in cov["parent_families"]))

    def test_incomplete_j7_stays_unknown(self):
        doc=json.loads((HIST/"I1"/"J07"/"matchday.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["completed_matches_in_archives"],0)
        self.assertEqual(doc["missing_results_before_cutoff"],1)
        self.assertTrue(doc["unresolved"][0]["never_infer_zero_goals"])

    def test_reproducible_content(self):
        with tempfile.TemporaryDirectory() as d:
            temp=Path(d)/"generated"
            result=build(cutoff=CUTOFF,output=temp)
            self.assertEqual(result["historical_matches"],120)
            original=(HIST/"E0"/"J06"/"matchday.json").read_bytes()
            repro=(temp/"E0"/"J06"/"matchday.json").read_bytes()
            self.assertEqual(original,repro)


if __name__=="__main__":
    unittest.main(verbosity=2)
