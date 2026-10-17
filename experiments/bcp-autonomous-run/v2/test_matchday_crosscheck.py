"""BCP October matchday cross-check offline acceptance tests."""
import datetime
import json
import unittest
import matchday_crosscheck as m

def source(score, date="2026-09-01", home="Arsenal FC"):
    return json.dumps({"name":"Test League","matches":[{"round":"Matchday 1",
            "date":date,"team1":home,"team2":"Leeds United FC",
            "score":{"ft":score}}]}).encode()

def csv_bytes(date="01/09/2026"):
    return ("Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\n"+
            f"{date},Arsenal,Leeds,2,1,H\n").encode()

class TestCrossCheck(unittest.TestCase):
    def test_sources_agree(self):
        r=m.run(csv_bytes(),source([2,1]),"E0",datetime.date(2026,10,17))
        self.assertEqual(r["csv_rows_reconciled"],1)
        self.assertEqual(r["scores_compared_with_matching_identity"],1)
        self.assertEqual(r["source_statuses"]["two_sources_agree"],1)
        self.assertEqual(r["anomalies"],[])

    def test_conflict_detected_not_overwritten(self):
        r=m.run(csv_bytes(),source([0,1]),"E0",datetime.date(2026,10,17))
        self.assertEqual(r["source_statuses"]["score_conflict"],1)
        self.assertEqual(r["anomalies"][0]["kind"],"score_conflict")

    def test_same_day_cannot_gain_score(self):
        r=m.run(csv_bytes("17/10/2026"),source([2,1],"2026-10-17"),
                "E0",datetime.date(2026,10,17))
        x=r["by_matchday"]["1"]["matches"][0]
        self.assertIsNone(x["score_football_data"])
        self.assertIsNone(x["score_openfootball"])
        self.assertEqual(r["eligible_csv_rows"],0)

    def test_unmapped_name_is_visible(self):
        r=m.run(csv_bytes(),source([2,1],home="Unverified Youth Club FC"),
                "E0",datetime.date(2026,10,17))
        self.assertEqual(r["unmapped_aliases"],["Unverified Youth Club FC"])
        self.assertEqual(r["csv_rows_reconciled"],0)
        self.assertTrue(any(a["kind"]=="fixture_not_reconciled" for a in r["anomalies"]))

    def test_input_can_be_repeated_deterministically(self):
        inputs=(csv_bytes(),source([2,1]),"E0",datetime.date(2026,10,17))
        self.assertEqual(m.run(*inputs),m.run(*inputs))

if __name__=="__main__":
    unittest.main(verbosity=2)
