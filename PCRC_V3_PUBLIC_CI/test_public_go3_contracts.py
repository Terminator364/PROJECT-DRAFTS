"""Public tests: synthetic data only; never checks a private repository."""
import unittest
from owner_profile_model import check_owner
from release_contract_model import check_release

OWNER = r"TESTDOMAIN\\Example"
HOME = r"C:\\Users\\Example"
HASH_A = "a" * 64
HASH_B = "b" * 64

def owner_fixture(**changes):
    base = {"identity": OWNER, "sid": "S-1-5-21-SYNTHETIC",
            "registry_profile": HOME, "userprofile": HOME, "python_home": HOME,
            "trusted_root_exists": True, "public_anchor_exists": True}
    base.update(changes)
    return base

def release_fixture(**changes):
    base = {"schema": "PCRC-PUBLIC-SYNTHETIC-1", "source_sha256": HASH_A,
            "archive_sha256": HASH_B, "manifest_member_hashes_verified": True,
            "tamper_rejected": True, "rollback_code_only": True,
            "current_db_preserved": True, "owner_grant_valid": True,
            "replay_rejected": True, "production_mutated": False}
    base.update(changes)
    return base

def admit(record=None, **changes):
    return check_release(record if record is not None else release_fixture(),
                         expected_source_sha=HASH_A,
                         official_signature_verified=changes.get("signed", True),
                         trusted_authority_verified=changes.get("trusted", True))

class OwnerProfileContract(unittest.TestCase):
    def test_valid_readonly(self):
        self.assertEqual(check_owner(owner_fixture(), OWNER)["state"],
                         "PROFILE_MATCHES_READONLY")
        self.assertFalse(check_owner(owner_fixture(), OWNER)["installation_allowed"])
    def test_owner_identity_wrong(self):
        self.assertEqual(check_owner(owner_fixture(identity="OTHER"), OWNER)["state"],
                         "HOLD_OWNER_MISMATCH")
    def test_sandbox_home_rejected(self):
        self.assertEqual(check_owner(owner_fixture(python_home=r"C:\\Temp\\Sandbox"), OWNER)["state"],
                         "HOLD_NONCANONICAL_PROFILE")
    def test_noncanonical_userprofile(self):
        self.assertEqual(check_owner(owner_fixture(userprofile=r"C:\\Temp\\Sandbox"), OWNER)["state"],
                         "HOLD_NONCANONICAL_PROFILE")
    def test_missing_identity(self):
        self.assertEqual(check_owner({}, OWNER)["state"], "HOLD_MISSING_IDENTITY")
    def test_traversal_rejected(self):
        self.assertEqual(check_owner(owner_fixture(userprofile=r"C:\\Users\\Example\\..\\Other"), OWNER)["state"],
                         "HOLD_INVALID_PROFILE")
    def test_missing_anchor(self):
        self.assertEqual(check_owner(owner_fixture(public_anchor_exists=False), OWNER)["state"],
                         "HOLD_TRUST_ANCHOR_MISSING")
    def test_missing_root(self):
        self.assertEqual(check_owner(owner_fixture(trusted_root_exists=False), OWNER)["state"],
                         "HOLD_ROOT_MISSING")
    def test_casefold(self):
        self.assertEqual(check_owner(owner_fixture(userprofile=r"c:\\users\\example",
                        python_home=r"c:\\users\\example"), OWNER)["state"],
                         "PROFILE_MATCHES_READONLY")

class ReleaseSafetyContract(unittest.TestCase):
    def test_good_synthetic_contract_no_install(self):
        result = admit()
        self.assertEqual(result["state"], "CONTRACT_MODEL_PASS")
        self.assertFalse(result["install_allowed"])
    def test_unsigned(self):
        self.assertEqual(admit(signed=False)["state"], "HOLD_UNVERIFIED_SIGNER")
    def test_untrusted_signer(self):
        self.assertEqual(admit(trusted=False)["state"], "HOLD_UNVERIFIED_SIGNER")
    def test_mismatched_source_pin(self):
        self.assertEqual(admit(release_fixture(source_sha256=HASH_B))["state"],
                         "HOLD_SOURCE_PIN_MISMATCH")
    def test_manifest_tamper_not_rejected(self):
        self.assertEqual(admit(release_fixture(tamper_rejected=False))["state"],
                         "HOLD_TAMPER_GATE")
    def test_missing_member_hash_verification(self):
        self.assertEqual(admit(release_fixture(manifest_member_hashes_verified=False))["state"],
                         "HOLD_UNVERIFIED_MEMBERS")
    def test_code_rollback_required(self):
        self.assertEqual(admit(release_fixture(rollback_code_only=False))["state"],
                         "HOLD_ROLLBACK_GATE")
    def test_preserve_live_db(self):
        self.assertEqual(admit(release_fixture(current_db_preserved=False))["state"],
                         "HOLD_CURRENT_DB_GATE")
    def test_owner_grant_required(self):
        self.assertEqual(admit(release_fixture(owner_grant_valid=False))["state"],
                         "HOLD_OWNER_AND_REPLAY_GATE")
    def test_replay_protection_required(self):
        self.assertEqual(admit(release_fixture(replay_rejected=False))["state"],
                         "HOLD_OWNER_AND_REPLAY_GATE")
    def test_no_production_modification(self):
        self.assertEqual(admit(release_fixture(production_mutated=True))["state"],
                         "HOLD_PRODUCTION_ISOLATION")
    def test_bad_hash_format(self):
        self.assertEqual(admit(release_fixture(source_sha256="not-hash"))["state"],
                         "HOLD_BAD_HASH_FORMAT")

if __name__ == "__main__":
    unittest.main()
