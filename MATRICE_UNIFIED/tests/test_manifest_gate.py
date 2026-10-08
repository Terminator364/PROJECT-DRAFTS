"""Zero-runner validation cases for the read-only migration gate."""
import unittest
from MATRICE_UNIFIED.tools.manifest_gate import audit


class ManifestGateTests(unittest.TestCase):
    def setUp(self):
        self.h = "a" * 64
        self.root = "/canonical"
        self.keep = {"id": "survivor", "action": "PRESERVE", "role": "ARCHIVE",
                     "sha256": self.h, "byte_verified": True}

    def case(self, *items):
        return audit({"canonical_root": self.root, "items": list(items)})

    def test_only_preserved_assets_pass(self):
        self.assertTrue(self.case(self.keep)["ok"])

    def test_verified_duplicate_with_survivor_can_pass_gate(self):
        duplicate = {"id": "copy", "action": "DELETE", "role": "ARCHIVE",
                     "sha256": self.h, "survivor_id": "survivor",
                     "byte_verified": True, "dependencies": []}
        self.assertTrue(self.case(self.keep, duplicate)["ok"])

    def test_no_sha_or_missing_byte_proof_blocks_delete(self):
        bad = {"id": "copy", "action": "DELETE", "survivor_id": "survivor"}
        self.assertFalse(self.case(self.keep, bad)["ok"])

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
