"""Tests for safe five-minute external data intake, no actual HTTP."""
import datetime as dt
import json
import pathlib
import tempfile
import unittest
import five_minute_provider as x

NOW=dt.datetime(2026,10,17,19,30,tzinfo=dt.timezone(dt.timedelta(hours=1)))
def event(status,stamp,home="Alpha",away="Beta"):
    return {"strStatus":status,"strTimestamp":stamp,"dateEvent":stamp[:10],
            "idEvent":"123","strHomeTeam":home,"strAwayTeam":away,
            "intHomeScore":"9","intAwayScore":"8","strVenue":"Example"}

class Tests(unittest.TestCase):
    def test_strips_live_and_completed_matches(self):
        raw={"events":[event("HT","2026-10-17T20:00:00"),
                       event("FT","2026-10-17T20:00:00"),
                       event("NS","2026-10-18T13:00:00")]}
        items,n=x.verify_and_filter(raw, NOW.astimezone(dt.timezone.utc))
        self.assertEqual(n,2)
        self.assertEqual(len(items),1)
        self.assertNotIn("intHomeScore",str(items))
        self.assertEqual(items[0]["scores_included"],False)

    def test_excludes_past_even_if_status_not_started(self):
        items,n=x.verify_and_filter({"events":[event("NS","2026-10-17T17:00:00")]},
                                    NOW.astimezone(dt.timezone.utc))
        self.assertEqual(items,[])
        self.assertEqual(n,1)

    def test_does_not_save_raw_live_data(self):
        def fake(league,day):
            return {"events":[event("1H","2026-10-18T13:00:00"),
                              event("NS","2026-10-18T13:00:00")]}
        with tempfile.TemporaryDirectory() as t:
            state={}
            snapshot=x.refresh(state,pathlib.Path(t),fetcher=fake,now=NOW)
            self.assertEqual(snapshot["request_count"],4)
            self.assertEqual(snapshot["counts"]["future_fixtures"],4)
            self.assertEqual(snapshot["counts"]["excluded_live_or_past"],4)
            text=(pathlib.Path(t)/"LATEST_PREMATCH.json").read_text(encoding="utf-8")
            self.assertNotIn('"1H"',text)
            self.assertNotIn("intHomeScore",text)
            self.assertEqual(state["network_request_count"],4)

    def test_missing_time_is_excluded(self):
        self.assertEqual(x.verify_and_filter({"events":[{"strStatus":"NS",
                       "strTimestamp":None}]})[0],[])

if __name__=="__main__":
    unittest.main(verbosity=2)
