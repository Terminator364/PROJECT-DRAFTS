"""Independent offline cross-audit for historical J1-J6, not an autonomous worker."""
import datetime
import json
import unittest
import historical_matchdays as m

def row(day,home,away,hg,ag):
    return {"_date":datetime.date.fromisoformat(day),
            "HomeTeam":home,"AwayTeam":away,
            "FTHG":str(hg),"FTAG":str(ag),
            "FTR":"H" if hg>ag else ("D" if hg==ag else "A"),
            "HS":"12","AS":"7","HxG":"1.4","AxG":"0.8"}

class CrossAuditHistorical(unittest.TestCase):
    def test_no_target_future_or_same_day(self):
        rows=[row("2026-08-21","Alpha","Beta",1,0),
              row("2026-08-22","Alpha","Gamma",0,4),
              row("2026-08-22","Delta","Alpha",5,0),
              row("2026-08-29","Alpha","Beta",9,8)]
        feat=m.team_history(rows,"Alpha",datetime.date(2026,8,22))
        self.assertEqual(feat["previous_games_strictly_before_calendar_day"],1)
        self.assertEqual(feat["historical_goals_for_last5_mean"],1)
        self.assertEqual(feat["historical_goals_against_last5_mean"],0)
        self.assertFalse(feat["same_day_results_used"])
        self.assertFalse(feat["target_match_outcome_used"])

    def test_first_game_no_prior(self):
        r=m.team_history([row("2026-08-21","A","B",9,9)],"A",datetime.date(2026,8,21))
        self.assertEqual(r["previous_games_strictly_before_calendar_day"],0)
        self.assertIsNone(r["historical_xg_last5_mean"])

    def test_all_120_files_and_day_crosswalk(self):
        out=m.TARGET
        matches=list(out.glob("*/J*/MATCHS/*.json"))
        reports=list(out.glob("*/J*/SOMMAIRE_JOURNEE.json"))
        crosswalk=list(out.glob("*/J*/COUVERTURE_62_ET_L3.json"))
        self.assertEqual(len(matches),120)
        self.assertEqual(len(reports),12)
        self.assertEqual(len(crosswalk),12)
        self.assertEqual(sum(len(json.loads(p.read_text(encoding="utf-8"))["families"])
                             for p in crosswalk),744)
        self.assertEqual(sum(sum(len(x["L3_children"]) for x in json.loads(p.read_text(encoding="utf-8"))["families"])
                             for p in crosswalk),1308)

    def test_no_false_prematch_evidence(self):
        for filename in m.TARGET.glob("*/J*/MATCHS/*.json"):
            d=json.loads(filename.read_text(encoding="utf-8"))
            self.assertEqual(d["snapshots"]["H0_ASOF_BEFORE_KICKOFF"]["status"],"NOT_RECONSTRUCTED")
            self.assertIsNone(d["provenance"]["original_published_at_utc"])
            self.assertFalse(d["usage"]["IC_scoring_permitted"])
            self.assertFalse(d["chronological_research_features"]["home"]["same_day_results_used"])
            self.assertFalse(d["chronological_research_features"]["away"]["same_day_results_used"])
            self.assertFalse(d["usage"]["may_use_target_result_as_feature"])
            self.assertFalse(d["usage"]["PIT_proven"])
            self.assertTrue(d["usage"]["training_label_available"])

    def test_rerun_histogram_is_stable(self):
        result=m.build()
        self.assertEqual(result["leagues"]["PREMIER_LEAGUE"]["matches_exported"],60)
        self.assertEqual(result["leagues"]["SERIE_A"]["matches_exported"],60)
        self.assertEqual(result["certified_operational_families"],0)
        self.assertEqual(result["l3_documented_children"],109)

if __name__=="__main__":
    unittest.main(verbosity=2)
