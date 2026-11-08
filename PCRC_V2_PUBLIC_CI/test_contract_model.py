"""Safe tests of public synthetic behavior, not production PCRC tests."""
import unittest
from contract_model import decide_operation, validate_public_payload, MAX_CHUNK_BYTES


class ContractTests(unittest.TestCase):
    def test_low_ram_keeps_control_available(self):
        for bytes_free in (0, 4096, 128 * 1024, 1 * 1024 * 1024):
            for operation in ("control", "journal"):
                self.assertEqual(decide_operation(available_bytes=bytes_free, operation=operation).action, "ACCEPT_LIGHTWEIGHT")

    def test_bulk_is_deferred_with_persistent_intent(self):
        for bytes_free in (0, 1024, 1024 * 1024, 7 * 1024 * 1024):
            self.assertEqual(decide_operation(available_bytes=bytes_free, operation="bulk").action, "DEFER_PERSISTENTLY")

    def test_bulk_chunk_is_bounded(self):
        for bytes_free in (8 * 1024 * 1024, 64 * 1024 * 1024, 1024 * 1024 * 1024):
            decision = decide_operation(available_bytes=bytes_free, operation="bulk")
            self.assertEqual(decision.action, "STREAM_BOUNDED")
            self.assertLessEqual(decision.chunk_bytes, MAX_CHUNK_BYTES)
            self.assertGreater(decision.chunk_bytes, 0)

    def test_invalid_operations_rejected(self):
        for operation in ("", "delete", "core_swap", "../config"):
            with self.assertRaises(ValueError):
                decide_operation(available_bytes=123, operation=operation)

    def test_public_payload_is_strict(self):
        specimen = {"case_id": "synthetic_01", "operation": "bulk", "available_bytes": 100, "expected_action": "DEFER_PERSISTENTLY"}
        validate_public_payload(specimen)
        for key in ("token", "hostname", "db_path", "private_key", "runtime_log"):
            with self.assertRaises(ValueError):
                validate_public_payload({**specimen, key: "redacted"})

    def test_negative_capacity_rejected(self):
        with self.assertRaises(ValueError):
            decide_operation(available_bytes=-1, operation="control")


if __name__ == "__main__":
    unittest.main()
