import unittest
from build_research_features import compute

class FeatureTests(unittest.TestCase):
    def test_event_time_cutoff(self):
        for code in ("E0","I1"):
            result=compute(code)
            self.assertEqual(result["n_fixtures"],70)
            for row in result["features"]:
                self.assertFalse(row["PIT_availability_verified"])
                self.assertEqual(row["status"],"OBSERVATION_ONLY_NO_IC")
                if row["max_evidence_date"]:
                    self.assertLess(row["max_evidence_date"],row["date"])

    def test_first_fixture_day_has_no_prior_current_season(self):
        for code in ("E0","I1"):
            rows=[row for row in compute(code)["features"] if row["matchday"]==1]
            first_date=min(row["date"] for row in rows)
            self.assertTrue(all(
                row["LEAGUE_BASE"]["historical_matches"]==0
                for row in rows if row["date"]==first_date))

    def test_seventh_round_only_uses_first_six(self):
        for code in ("E0","I1"):
            seventh=[row for row in compute(code)["features"] if row["matchday"]==7]
            self.assertEqual(len(seventh),10)
            self.assertTrue(all(row["LEAGUE_BASE"]["historical_matches"]==60 for row in seventh))
            self.assertTrue(all(row["max_evidence_date"]=="2026-10-12" for row in seventh))

if __name__=="__main__":
    unittest.main(verbosity=2)
