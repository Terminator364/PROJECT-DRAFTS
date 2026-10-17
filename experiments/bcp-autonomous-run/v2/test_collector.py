"""Offline tests for V2 collector: strict cutoff, validation, archive immutability."""
import csv
import io
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import collector

def sample():
    return ("Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS\n"
            "01/08/2025,Alpha,Beta,2,1,H,10,8\n"
            "02/08/2025,Gamma,Delta,0,0,D,5,5\n"
            "03/08/2025,Alpha,Beta,0,3,A,4,8\n"
            "01/12/2026,Gamma,Alpha,5,4,H,14,10\n").encode()

class TestCollector(unittest.TestCase):
    def test_cutoff_blocks_future(self):
        record=collector.audit(sample(),collector.dt.date(2026,10,17))
        self.assertEqual(record["accepted_historical"],3)
        self.assertEqual(record["invalid_rows"],0)
        self.assertEqual(record["over15_frequency"],round(2/3,6))
        self.assertFalse(record["pit_certified"])

    def test_cutoff_blocks_target_day(self):
        record=collector.audit(sample(),collector.dt.date(2025,8,2))
        self.assertEqual(record["accepted_historical"],1)

    def test_malformed_result_rejected(self):
        bad=b"Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\n01/08/2025,A,B,2,0,A\n"
        record=collector.audit(bad,collector.dt.date(2026,10,17))
        self.assertEqual(record["accepted_historical"],0)
        self.assertEqual(record["invalid_rows"],1)

    def test_missing_columns_rejected(self):
        with self.assertRaises(ValueError):
            collector.audit(b"Date,HomeTeam\n01/08/2025,A\n",collector.dt.date(2026,10,17))

    def test_duplicate_rejected(self):
        lines=sample().decode().splitlines()
        raw=("\n".join(lines[:2]+lines[1:2])+"\n").encode()
        audit=collector.audit(raw,collector.dt.date(2026,10,17))
        self.assertEqual(audit["accepted_historical"],1)
        self.assertEqual(audit["invalid_rows"],1)

    def test_62_registry_is_observation_only(self):
        reg=json.loads((pathlib.Path(__file__).parent/"matrice_62_registry.json").read_text(encoding="utf-8"))
        self.assertEqual(len(reg["families"]),62)
        self.assertEqual(len({x["id"] for x in reg["families"]}),62)
        self.assertTrue(all(x["ic_effect"]=="DISABLED" for x in reg["families"]))

    def test_mocked_ten_sources_and_content_addressing(self):
        reg=json.loads((pathlib.Path(__file__).parent/"matrice_62_registry.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)
            (root/"raw").mkdir()
            state={"run_id":"OFFLINE-TEST","sources":{}}
            with patch.object(collector,"fetch",return_value=sample()):
                collector.cycle(root,state,reg)
                self.assertEqual(len(state["sources"]),10)
                self.assertEqual(len(list((root/"raw").glob("*.csv"))),1)
                self.assertEqual(json.loads((root/"coverage_62.json").read_text())["total_families"],62)
                a=json.loads((root/"manifest.json").read_text())
                self.assertEqual(a["total_historical_matches"],30)
                self.assertEqual(a["changed_sources"],10)
                collector.cycle(root,state,reg)
                a=json.loads((root/"manifest.json").read_text())
                self.assertEqual(a["changed_sources"],0)

if __name__=="__main__":
    unittest.main(verbosity=2)
