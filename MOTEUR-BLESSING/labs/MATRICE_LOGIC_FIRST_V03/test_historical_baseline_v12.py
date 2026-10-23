"""D066: chronological leakage and honest Brier backtest tests, synthetic test fixtures."""
import copy
from datetime import datetime,timedelta,timezone
import unittest
import historical_baseline_v12 as m

def records(n=64):
    base=datetime(2025,1,1,tzinfo=timezone.utc)
    teams=["A","B","C","D"]
    rows=[]
    for i in range(n):
        kickoff=base+timedelta(days=i)
        end=kickoff+timedelta(hours=2)
        issued=end+timedelta(hours=1)
        h=teams[i%4];a=teams[(i%4+1+i//4%3)%4]
        if h==a:a=teams[(i%4+2)%4]
        rows.append({"fixture_id":"HIST-%03d"%i,"home_team":h,"away_team":a,
                     "kickoff_utc":kickoff.isoformat(),"final_whistle_utc":end.isoformat(),
                     "source_issued_utc":issued.isoformat(),
                     "source_first_seen_utc":(issued+timedelta(minutes=5)).isoformat(),
                     "home_goals":i%4,"away_goals":(i*2+1)%3})
    return rows

def fixture():
    return {"fixture_id":"TARGET","home_team":"A","away_team":"B",
            "analysis_asof_utc":"2025-03-15T12:00:00+00:00",
            "kickoff_utc":"2025-03-16T14:00:00+00:00"}

class TestEmpiricalPrematchBaseline(unittest.TestCase):
    def test_finite_calculated_not_calibrated(self):
        out=m.predict(fixture(),records())
        self.assertEqual(out["status"],"BASELINE_PREMATCH_ESTIMATE_UNVALIDATED")
        self.assertTrue(0<out["P_over15"]<1)
        self.assertIsNone(out["predictive_accuracy_percent"])
        self.assertFalse(out["calibration_verified"])
        self.assertEqual(out["R8_children_assigned_nonzero_coefficients"],0)
    def test_final_result_observed_only_after_original_publisher_first_seen(self):
        base=m.predict(fixture(),records())
        later=copy.deepcopy(records()[0])
        later["fixture_id"]="LATE-PUBLISHED"
        later["source_issued_utc"]="2025-03-20T00:00:00+00:00"
        later["source_first_seen_utc"]="2025-03-20T01:00:00+00:00"
        changed=m.predict(fixture(),records()+[later])
        self.assertEqual(base["IC_over15_percent"],changed["IC_over15_percent"])
        self.assertEqual(base["eligible_games"],changed["eligible_games"])
        self.assertEqual(changed["excluded_late_or_target_games"],base["excluded_late_or_target_games"]+1)
    def test_target_fixture_same_id_excluded_even_if_previously_published(self):
        h=records()
        game={**h[0],"fixture_id":"TARGET"}
        before=m.predict(fixture(),h)
        after=m.predict(fixture(),h+[game])
        self.assertEqual(before["eligible_games"],after["eligible_games"])
    def test_no_source_is_abstention_not_zero_percent(self):
        pred=m.predict(fixture(),[])
        self.assertEqual(pred["status"],"ABSTAIN_NOT_ENOUGH_PIT_HISTORICAL_MATCHES")
        self.assertIsNone(pred["IC_over15_percent"])
    def test_team_new_to_league_is_abstention(self):
        f={**fixture(),"home_team":"UNSEEN"}
        self.assertEqual(m.predict(f,records())["status"],"ABSTAIN_NO_BOTH_TEAM_HISTORIES")
    def test_future_kickoff_rejected(self):
        f={**fixture(),"analysis_asof_utc":"2025-03-16T15:00:00+00:00"}
        with self.assertRaisesRegex(m.HistoricalEvidenceError,"TARGET_CUTOFF"):
            m.predict(f,records())
    def test_duplicate_provenance_and_inconsistent_times_fail(self):
        h=records()
        with self.assertRaisesRegex(m.HistoricalEvidenceError,"DUPLICATE"):
            m.predict(fixture(),h+[h[0]])
        h=records()
        h[0]["source_first_seen_utc"]="2024-11-15T00:00:00+00:00"
        with self.assertRaisesRegex(m.HistoricalEvidenceError,"INVALID_HISTORICAL_EVENT_PROVENANCE"):
            m.predict(fixture(),h)
    def test_synthetic_or_inplay_source_forbidden(self):
        h=records();h[0]["synthetic"]=True
        with self.assertRaisesRegex(m.HistoricalEvidenceError,"NO_SYNTHETIC"):
            m.predict(fixture(),h)
    def test_bool_float_and_negative_goal_rejected(self):
        for invalid in (-1,2.5,True):
            h=records();h[0]["home_goals"]=invalid
            with self.subTest(v=str(invalid)),self.assertRaisesRegex(m.HistoricalEvidenceError,"INVALID_GOALS"):
                m.predict(fixture(),h)
    def test_walkforward_is_retro_only_and_does_not_claim_independent_calibration(self):
        out=m.walkforward(records(),minimum_games=24)
        self.assertGreater(out["test_predictions"],0)
        self.assertTrue(0<=out["brier"]<=1)
        self.assertGreaterEqual(out["logloss"],0)
        self.assertFalse(out["independent_external_validation"])
        self.assertIn("NOT_PROOF",out["status"])
    def test_wrong_history_clock_fails(self):
        bad=records();bad[0]["source_issued_utc"]="not-a-date"
        with self.assertRaisesRegex(m.HistoricalEvidenceError,"INVALID_EVIDENCE_TIMESTAMP"):
            m.predict(fixture(),bad)
    def test_only_live_t0_can_generate_prediction(self):
        h=records();f=fixture();f["fixture_id"]=h[20]["fixture_id"]
        result=m.predict(f,h)
        self.assertNotIn(h[20]["fixture_id"],[x["fixture_id"] for x in h if x["fixture_id"]==f["fixture_id"] and False])
        self.assertEqual(result["source_games_total"],len(h))

if __name__=="__main__":unittest.main()
