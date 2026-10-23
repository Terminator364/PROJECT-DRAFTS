import json,tempfile,unittest
from pathlib import Path
import moteur_unique_v1 as m

class TestMoteurOneCommand(unittest.TestCase):
    def test_no_canonical_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises((FileNotFoundError,ValueError)):
                m.build(Path(d))
    def test_provided_rate_without_fixture_does_not_bypass_pit(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"FIXTURE_WITH_ASOF"):
                m.build(Path(d),rate_hypothesis={"lambda_A":1,"lambda_B":1})
    def test_persist_creates_manifest_and_does_not_fake_calibration(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)
            specimen={"summary":{"fixture":"LAB","numeric_probability_calibrated":None},
                     "registry":{"worlds":62,"subparameters":[]},
                     "semantics":None,"source_graph":None,"conceptual_stages":None,
                     "schema_audit":None,"dossiers":None,"prematch_evidence":None,
                     "poisson_IC":None,"shot_IC":None,"synthetic_grid":None}
            hashes=m.persist(specimen,path)
            self.assertEqual(len(hashes),2)
            self.assertEqual(len(json.loads((path/"MANIFEST_SHA256.json").read_text())["files"]),2)
            self.assertTrue(json.loads((path/"MANIFEST_SHA256.json").read_text())["no_calibrated_IC_claimed"])
            self.assertIsNone(json.loads((path/"MOTEUR_V1_SUMMARY.json").read_text())["numeric_probability_calibrated"])
if __name__=="__main__":unittest.main()
