"""Offline tests for J1-current history-first TheSportsDB backfill."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import historical_provider_backfill as h

CUTOFF=dt.date(2026,10,17)
class BackfillTests(unittest.TestCase):
    def test_schedule_rejects_current_and_future(self):
        pairs, known=h.schedule(CUTOFF)
        self.assertTrue(pairs)
        self.assertTrue(all(dt.date.fromisoformat(day)<CUTOFF for day,code in pairs))
        self.assertEqual(pairs,sorted(pairs))
        self.assertTrue(set(x[1] for x in pairs)=={"E0","I1"})

    def test_fulltime_results_are_postmatch_only(self):
        pairs,known=h.schedule(CUTOFF)
        day,code=pairs[0]
        example=next(k for k in known[code] if k[0]==day and known[code][k] is not None)
        goals=known[code][example]
        x={"events":[{"dateEvent":day,"strStatus":"FT",
                      "strHomeTeam":example[1],"strAwayTeam":example[2],
                      "intHomeScore":str(goals[0]),"intAwayScore":str(goals[1]),"idEvent":"117",
                      "intRound":"1"}]}
        audit=h.filter_and_reconcile(x,code,day,known[code],CUTOFF)
        self.assertEqual(len(audit["matched"]),1)
        match=audit["matched"][0]
        self.assertEqual(match["comparison"],"AGREES_WITH_ARCHIVED_CSV")
        self.assertEqual(match["status"],"POSTMATCH_HISTORICAL_ONLY")
        self.assertTrue(match["not_prematch_feature_for_target"])
        self.assertIsNone(match["historical_available_at_j_minus_n"])

    def test_live_current_future_ignored(self):
        day="2026-10-18"
        payload={"events":[{"dateEvent":day,"strStatus":"FT","strHomeTeam":"A",
                "strAwayTeam":"B","intHomeScore":"3","intAwayScore":"0"},
            {"dateEvent":"2026-10-10","strStatus":"HT","strHomeTeam":"A",
             "strAwayTeam":"B","intHomeScore":"3","intAwayScore":"0"}]}
        x=h.filter_and_reconcile(payload,"E0",day,{},CUTOFF)
        self.assertEqual(x["matched"],[])
        self.assertEqual(x["unmatched"],[])

    def test_four_requests_in_cycle_and_no_reread_same_day(self):
        with tempfile.TemporaryDirectory() as folder:
            calls=[]
            def fake(code,day):
                calls.append(code+"|"+day)
                return b'{"events":[]}'
            state={}
            with patch.object(h,"OUT",Path(folder)):
                report=h.refresh(state,cutoff=CUTOFF,fetcher=fake,max_requests=4)
                self.assertEqual(report["this_cycle_http_requests"],4)
                self.assertEqual(report["date_tasks_validated"],4)
                self.assertEqual(len(state["historical_checked"]),4)
                report2=h.refresh(state,cutoff=CUTOFF,fetcher=fake,max_requests=4)
                self.assertEqual(report2["date_tasks_validated"],8)
                self.assertEqual(len(set(calls)),8)
                self.assertTrue(report2["no_live_or_future"])
                self.assertFalse(report2["original_historical_published_at_verified"])

if __name__=="__main__":
    unittest.main(verbosity=2)
