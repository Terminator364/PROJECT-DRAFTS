import copy,math,unittest
import temporal_backtest_v12 as x

def row(fid,p,goals,kind="SYNTHETIC_TEST_DATA"):
    return {"fixture_id":fid,"kickoff_utc":"2026-10-23T19:00:00Z",
            "analysis_asof_utc":"2026-10-22T12:00:00Z",
            "prediction_frozen_utc":"2026-10-22T11:00:00Z",
            "result_available_utc":"2026-10-23T22:00:00Z",
            "horizon":"J-1","p_over15_frozen":p,
            "goals_A_final":goals,"goals_B_final":0,
            "provenance_kind":kind}

class TestFreezeFirstBenchmark(unittest.TestCase):
    def test_honest_synthetic_brier_and_logloss(self):
        d=x.score([row("one",.5,2),row("two",.5,0)])
        self.assertAlmostEqual(d["brier_score"],.25,places=12)
        self.assertAlmostEqual(d["log_loss"],math.log(2),places=12)
        self.assertAlmostEqual(d["expected_calibration_error_10_bins"],0.0,places=12)
        self.assertEqual(d["unique_target_fixtures"],2)
        self.assertFalse(d["empirical_real_match_validation_completed"])
        self.assertIsNone(d["accuracy_claim_percent"])
    def test_duplicate_fixture_blocked(self):
        with self.assertRaisesRegex(x.ReplayError,"DUPLICATE_FIXTURE"):
            x.score([row("one",.5,2),row("one",.4,0)])
    def test_future_prediction_freeze_blocked(self):
        r=row("one",.5,2)
        r["prediction_frozen_utc"]="2026-10-23T20:00:00Z"
        with self.assertRaisesRegex(x.ReplayError,"TEMPORAL_LEAK"):x.score([r])
    def test_pretended_result_known_pre_kickoff_blocked(self):
        r=row("one",.5,2)
        r["result_available_utc"]="2026-10-23T18:00:00Z"
        with self.assertRaisesRegex(x.ReplayError,"TEMPORAL_LEAK"):x.score([r])
    def test_target_match_feature_leak_blocked(self):
        r=row("one",.5,2)
        r["contains_target_match_inplay_inputs"]=True
        with self.assertRaisesRegex(x.ReplayError,"FEATURE_LEAK"):x.score([r])
    def test_invalid_probability_not_clamped_into_truth(self):
        for v in (True,-.2,1.2,".8",float("nan")):
            with self.subTest(value=str(v)),self.assertRaises(x.ReplayError):
                x.score([row("one",v,2)])
    def test_mixed_source_label_never_proves_validation(self):
        with self.assertRaisesRegex(x.ReplayError,"MIXED_HISTORIC_AND_SYNTHETIC"):
            x.score([row("one",.8,2),row("two",.7,0,"CLAIMED_HISTORICAL_NOT_INDEPENDENTLY_VERIFIED")])
    def test_historical_label_unverified_by_itself(self):
        d=x.score([row("one",.8,2,"CLAIMED_HISTORICAL_NOT_INDEPENDENTLY_VERIFIED")])
        self.assertFalse(d["original_external_source_provenance_independently_verified"])
        self.assertFalse(d["empirical_real_match_validation_completed"])
if __name__=="__main__":unittest.main()
