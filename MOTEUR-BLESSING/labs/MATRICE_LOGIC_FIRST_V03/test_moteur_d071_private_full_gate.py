"""D071 safety and honesty tests; no private data exposed on public CI."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import moteur_d071_private_full_gate as gate

class TestD071PrivateTrueOriginalGate(unittest.TestCase):
    def test_no_missing_originals_can_get_a_pass_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with patch.object(gate.m,"build",side_effect=FileNotFoundError(
                    "ORIGINAL_R8_PRIVATE_NOT_AVAILABLE")):
                rc=gate.run(root,root/"output",root/"receipt.json")
            self.assertEqual(rc,1)
            report=json.loads((root/"receipt.json").read_text())
            self.assertEqual(report["readiness"],"FAIL_SOURCE_E2E")
            self.assertFalse(report["e2e_pass"])
            self.assertIsNone(report["sporting_predictive_accuracy"])
            self.assertIn("ORIGINAL_R8_PRIVATE",report["error"])
    def test_bad_evidence_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"R8_NATIVE_OPERATIONAL_355_PRIVATE.json").write_bytes(b"contract")
            (root/"IC_THEORETICAL_GRID_1000.json").write_bytes(b"grid")
            files={x:hashlib.sha256((root/x).read_bytes()).hexdigest()
                   for x in ("R8_NATIVE_OPERATIONAL_355_PRIVATE.json",
                             "IC_THEORETICAL_GRID_1000.json")}
            (root/"MANIFEST_SHA256.json").write_text(json.dumps({
                "files":files,"no_calibrated_IC_claimed":True}))
            self.assertEqual(gate.verify_manifest(root,files)["verified_manifest_files"],2)
            (root/"R8_NATIVE_OPERATIONAL_355_PRIVATE.json").write_bytes(b"tampered")
            with self.assertRaisesRegex(gate.IntegrationGateFailed,"SHA256_MISMATCH"):
                gate.verify_manifest(root,files)
    def test_synthetic_source_shaped_data_must_not_pass_original_gate(self):
        from test_moteur_unique_d071_e2e_mocked_source import (
            TestD071SyntheticFullOrchestration)
        result,_,_=TestD071SyntheticFullOrchestration().run_pipeline()
        with self.assertRaises(gate.IntegrationGateFailed):
            gate.verify_original_355(result)
    def test_lab_inputs_never_claim_real_match(self):
        self.assertIn("SYNTHETIC",gate.FIXTURE["fixture_id"])
        self.assertEqual(gate.RATES["source_kind"],"SYNTHETIC_ASSUMPTION_ONLY")
        self.assertEqual(gate.SHOTS["projection_kind"],"HYPOTHETICAL_PRET0_SHOT_EVENTS")

if __name__=="__main__":unittest.main()
