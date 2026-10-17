import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"outputs"
CUT="2026-10-17"

class TwoFavoritesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((DATA/"ROUNDWISE_MANIFEST.json").read_text(encoding="utf8"))

    def test_two_favorites_and_14_round_snapshots(self):
        self.assertEqual(set(self.manifest["leagues"]),{"E0","I1"})
        for code,meta in self.manifest["leagues"].items():
            self.assertEqual(len(meta["matchdays_from_current_backwards"]),7)
            self.assertEqual([v["matchday"] for v in meta["matchdays_from_current_backwards"]],[7,6,5,4,3,2,1])
            for n in range(1,8):
                obj=json.loads((DATA/f"{code}_matchday_{n:02d}.json").read_text(encoding="utf8"))
                self.assertEqual(len(obj["fixtures"]),10)

    def test_cutoff_prevents_same_day_final_scores(self):
        for code in ("E0","I1"):
            for n in range(1,8):
                obj=json.loads((DATA/f"{code}_matchday_{n:02d}.json").read_text(encoding="utf8"))
                for record in obj["fixtures"]:
                    if record["date"]>=CUT:
                        self.assertIsNone(record["historical_score"])
                        self.assertEqual(record["status"],"ON_OR_AFTER_CUTOFF_NO_RESULTS_ADMITTED")

    def test_cross_source_agreement_and_missingness_are_explicit(self):
        for code,meta in self.manifest["leagues"].items():
            self.assertEqual(meta["two_source_result_agreements"],50)
            self.assertEqual(meta["score_conflicts"],0)
            self.assertEqual(meta["football_data_rows_unmatched"],0)
            r=meta["matchdays_from_current_backwards"]
            self.assertEqual(r[1]["statuses"],{"CSV_RESULT_ONLY":10})
            for round_info in r[2:]:
                self.assertEqual(round_info["statuses"],{"TWO_SOURCE_RESULT_AGREEMENT":10})

    def test_official_observations_are_traceable_and_do_not_set_IC(self):
        total=0
        for code in ("E0","I1"):
            document=json.loads((DATA/f"{code}_matchday_07.json").read_text(encoding="utf8"))
            for r in document["fixtures"]:
                if "REFEREE_official" in r:
                    total+=1
                    e=r["REFEREE_official"]
                    self.assertLess(e["published_day"],r["date"])
                    self.assertEqual(e["historical_PIT_replay"],"NOT_CERTIFIED")
                    self.assertTrue(e["source_url"].startswith("https://"))
                if "official_score_postevent_observation" in r:
                    self.assertFalse(r["official_score_postevent_observation"]["admissible_for_prematch_of_same_fixture"])
                    self.assertIsNone(r["historical_score"])
        self.assertEqual(total,12)

    def test_provenance_and_metadata(self):
        self.assertEqual(self.manifest["cutoff_exclusive"],CUT)
        self.assertIn("RESEARCH_ONLY",self.manifest["scientific_status"])
        for code,meta in self.manifest["leagues"].items():
            self.assertEqual(len(meta["openfootball_sha256"]),64)
            self.assertEqual(meta["openfootball_total_season_fixtures"],380)
            self.assertEqual(meta["football_data_cached_rows_prior_to_cutoff"],60)
            self.assertIn("UNVERIFIED",meta["data_quality_warning"].upper())

if __name__=="__main__":
    unittest.main(verbosity=2)
