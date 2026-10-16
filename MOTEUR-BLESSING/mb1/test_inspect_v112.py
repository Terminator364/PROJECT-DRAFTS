#!/usr/bin/env python3
"""Tests de sécurité/inventaire MB-1, données purement fictives."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

from inspect_v112 import AuditError, REQUIRED, inspect


def zip_bytes(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files:
            zf.writestr(name, data)
    return b.getvalue()


def valid_files():
    return [
        (name, json.dumps({"probe": [1, 2, 3]}) if name.endswith(".json") else "fiction")
        for name in REQUIRED
    ]


class TestMB1Audit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "test.zip"

    def run_archive(self, files, **opts):
        raw = zip_bytes(files)
        self.archive.write_bytes(raw)
        return inspect(
            self.archive,
            expected_sha=opts.get("sha", hashlib.sha256(raw).hexdigest()),
            expected_size=opts.get("size", len(raw)),
        )

    def test_complete_structure_is_not_sporting_validation(self):
        r = self.run_archive(valid_files())
        self.assertEqual(r["structure_status"], "COMPLETE")
        self.assertEqual(r["required_present"], 8)
        self.assertFalse(r["PIT_sources_validated"])
        self.assertFalse(r["sporting_performance_validated"])
        self.assertFalse(r["score_activation_allowed"])

    def test_partial_structure_fails_closed(self):
        r = self.run_archive([("00_LIRE_EN_PREMIER.md", "texte")])
        self.assertEqual(r["structure_status"], "INCOMPLETE")
        self.assertIn("code/moteur_v112.py", r["missing"])

    def test_wrong_sha_rejected(self):
        with self.assertRaisesRegex(AuditError, "SHA256"):
            self.run_archive(valid_files(), sha="0" * 64)

    def test_wrong_size_rejected(self):
        with self.assertRaisesRegex(AuditError, "Taille"):
            self.run_archive(valid_files(), size=5)

    def test_path_traversal_rejected(self):
        with self.assertRaisesRegex(AuditError, "Chemin"):
            self.run_archive(valid_files() + [("../outside.txt", "bad")])

    def test_windows_drive_path_rejected(self):
        with self.assertRaisesRegex(AuditError, "Chemin"):
            self.run_archive([("C:/temp/evil.txt", "bad")])

    def test_backslash_rejected(self):
        with self.assertRaisesRegex(AuditError, "Chemin"):
            self.run_archive([("..\\evil.txt", "bad")])

    def test_duplicate_names_rejected(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with self.assertRaisesRegex(AuditError, "dupliques"):
                self.run_archive(valid_files() + [valid_files()[0]])

    def test_broken_json_rejected(self):
        files = [(name, "{" if name.endswith(".json") else "fiction") for name in REQUIRED]
        with self.assertRaisesRegex(AuditError, "JSON invalide"):
            self.run_archive(files)

    def test_forged_receipt_does_not_imply_valid_engine(self):
        r = self.run_archive(valid_files())
        self.assertFalse(r["actual_62_240_140_372_mappings_validated"])

    def test_missing_file_refused(self):
        with self.assertRaisesRegex(AuditError, "Archive absente"):
            inspect(self.archive)


if __name__ == "__main__":
    unittest.main(verbosity=2)
