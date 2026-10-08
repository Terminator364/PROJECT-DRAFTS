"""Zero-runner validation cases for the read-only migration gate."""
import unittest
import hashlib
import tempfile
from pathlib import Path
from MATRICE_UNIFIED.tools.manifest_gate import audit


class ManifestGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.original = Path(self.temp.name) / "original.bin"
        self.copy = Path(self.temp.name) / "copy.bin"
        self.original.write_bytes(b"same-content")
        self.copy.write_bytes(b"same-content")
        self.h = hashlib.sha256(b"same-content").hexdigest()
        self.root = "/canonical"
        self.keep = {"id": "survivor", "action": "PRESERVE", "role": "ARCHIVE",
                     "sha256": self.h, "local_file": str(self.original)}

    def case(self, *items):
        return audit({"canonical_root": self.root, "items": list(items)})

    def test_only_preserved_assets_pass(self):
        self.assertTrue(self.case(self.keep)["ok"])

    def test_verified_duplicate_with_survivor_can_pass_gate(self):
        duplicate = {"id": "copy", "action": "DELETE", "role": "ARCHIVE",
                     "sha256": self.h, "survivor_id": "survivor",
                     "local_file": str(self.copy), "reference_scan_complete": True, "dependencies": []}
        self.assertTrue(self.case(self.keep, duplicate)["ok"])

    def test_no_sha_or_missing_byte_proof_blocks_delete(self):
        bad = {"id": "copy", "action": "DELETE", "survivor_id": "survivor"}
        self.assertFalse(self.case(self.keep, bad)["ok"])

    def test_hash_flag_cannot_replace_actual_bytes(self):
        fake = {"id": "copy", "action": "DELETE", "role": "ARCHIVE", "sha256": self.h,
                "survivor_id": "survivor", "byte_verified": True,
                "reference_scan_complete": True}
        self.assertFalse(self.case(self.keep, fake)["ok"])

    def test_active_authority_prefix_blocked(self):
        x = {"id": "live", "action": "MOVE", "role": "ACTIVE_AUTHORITY",
             "target_path": "/canonical/live", "readback_id_match": True}
        self.assertFalse(self.case(x)["ok"])

    def test_worker_absolute_path_blocks_move(self):
        worker = {"id": "worker", "action": "MOVE", "role": "ARCHIVE",
                  "target_path": "/canonical/worker", "readback_id_match": True,
                  "absolute_path_reference": True}
        self.assertFalse(self.case(worker)["ok"])

    def test_active_roles_are_immutable(self):
        x = {"id": "live", "action": "MOVE", "role": "ACTIVE",
             "target_path": "/canonical/live", "readback_id_match": True}
        self.assertFalse(self.case(x)["ok"])

    def test_path_escape_is_rejected(self):
        x = {"id": "escape", "action": "MOVE", "target_path": "/canonical/../outside",
             "readback_id_match": True}
        self.assertFalse(self.case(x)["ok"])

    def test_no_readback_rejected(self):
        x = {"id": "unverified", "action": "MOVE", "target_path": "/canonical/check"}
        self.assertFalse(self.case(x)["ok"])

    def test_duplicate_identifiers_rejected(self):
        self.assertFalse(self.case(self.keep, dict(self.keep))["ok"])

    def test_overwrite_never_allowed(self):
        self.assertFalse(self.case({"id": "x", "action": "OVERWRITE"})["ok"])


if __name__ == "__main__":
    unittest.main()
