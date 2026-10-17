"""Offline acceptance suite for historical horizon ledgers; no remote source calls."""
import datetime as dt
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DIR=ROOT/"05_JOURNEES"/"HISTORIQUE_J1_ACTUEL"

class HorizonAuditTests(unittest.TestCase):
    def test_720_horizons_and_zero_certified_pit(self):
        idx=json.loads((DIR/"INDEX_HORIZONS_NON_CERTIFIES.json").read_text(encoding="utf-8"))
        self.assertEqual(idx["horizon_records_total"],720)
        self.assertEqual(idx["matches_total"],120)
        self.assertTrue(idx["postgame_outcome_never_in_target_features"])
        self.assertEqual(idx["status"],"RESEARCH_DESIGN_ONLY_NOT_PIT_CERTIFIED")

    def test_no_target_label_or_future_history_in_horizons(self):
        all_records={}
        for code in ("E0","I1"):
            for round_id in range(1,7):
                src=json.loads((DIR/code/f"J{round_id:02d}"/"matchday.json").read_text(encoding="utf-8"))
                for game in src["matches"]:
                    all_records[game["fixture_key_local"]]=game
        checked=0
        for code in ("E0","I1"):
            for round_id in range(1,7):
                f=DIR/code/f"J{round_id:02d}"/"REPLAY_HORIZONS_RECHERCHE.json"
                obj=json.loads(f.read_text(encoding="utf-8"))
                self.assertTrue(obj["date_only_design_not_historical_point_in_time"])
                self.assertEqual(len(obj["horizon_records"]),10)
                for line in obj["horizon_records"]:
                    self.assertEqual(len(line["horizons"]),6)
                    target=line["fixture_key_local"]
                    for horizon in line["horizons"]:
                        checked+=1
                        self.assertFalse(horizon["target_game_final_score_in_inputs"])
                        self.assertIsNone(horizon["utc_asof_instant"])
                        self.assertNotIn("over15_fulltime_training_label",horizon)
                        self.assertNotIn("full_time_goals",horizon)
                        self.assertFalse(horizon["source_calendar_availability_assumed"])
                        cutoff=dt.date.fromisoformat(horizon["calendar_cutoff_date_exclusive"])
                        hist=horizon["candidate_training_history"]
                        home=hist["home_team_history_candidates"]
                        away=hist["away_team_history_candidates"]
                        self.assertNotIn(target,home)
                        self.assertNotIn(target,away)
                        for ref in home+away:
                            prior=dt.date.fromisoformat(
                                all_records[ref]["prematch_identity_observed_in_current_archive"]["date"])
                            self.assertLess(prior,cutoff)
        self.assertEqual(checked,720)

if __name__=="__main__":
    unittest.main(verbosity=2)
