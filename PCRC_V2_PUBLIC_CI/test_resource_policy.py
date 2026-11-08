"""Portable executable tests of identical private/public low-memory policy."""
import unittest

try:
    from continuity_v2.resource_policy import (
        plan_operation, MIB, MAX_BULK_CHUNK_BYTES, BULK_HEADROOM_BYTES
    )
except ModuleNotFoundError as exc:
    if exc.name != "continuity_v2":
        raise
    from resource_policy import (
        plan_operation, MIB, MAX_BULK_CHUNK_BYTES, BULK_HEADROOM_BYTES
    )


class ResourcePolicyTests(unittest.TestCase):
    def call(self, available, operation="control", total=4096*MIB):
        return plan_operation(total_bytes=total, available_bytes=available,
                              operation=operation)

    def test_99_percent_used_does_not_reject_control(self):
        d = self.call(4096*MIB // 100)
        self.assertEqual(d.memory_used_percent, 99)
        self.assertEqual(d.action, "ATTEMPT_LIGHTWEIGHT")
        self.assertFalse(d.executed)

    def test_99_percent_used_does_not_reject_receipt(self):
        self.assertEqual(self.call(4096*MIB // 100, "receipt").action,
                         "ATTEMPT_LIGHTWEIGHT")

    def test_zero_free_ram_is_not_false_success(self):
        d = self.call(0)
        self.assertEqual(d.action, "ATTEMPT_LIGHTWEIGHT")
        self.assertFalse(d.executed)

    def test_99_percent_used_bulk_is_deferred_not_lost(self):
        d = self.call(4096*MIB // 100, "bulk")
        self.assertEqual(d.action, "DEFER_HEAVY")
        self.assertTrue(d.action_requires_durable_queue)
        self.assertEqual(d.chunk_bytes, 0)

    def test_low_memory_bulk_is_deferred(self):
        for free in (0, 1, 4*MIB, 127*MIB):
            with self.subTest(free=free):
                self.assertEqual(self.call(free, "bulk").action, "DEFER_HEAVY")

    def test_bulk_threshold_is_explicit(self):
        self.assertEqual(self.call(BULK_HEADROOM_BYTES - 1, "bulk").action, "DEFER_HEAVY")
        self.assertEqual(self.call(BULK_HEADROOM_BYTES, "bulk").action, "ALLOW_CHUNKED")

    def test_bulk_chunks_bounded(self):
        for free in (128*MIB, 200*MIB, 4096*MIB):
            with self.subTest(free=free):
                d = self.call(free, "bulk")
                self.assertEqual(d.action, "ALLOW_CHUNKED")
                self.assertTrue(0 < d.chunk_bytes <= MAX_BULK_CHUNK_BYTES)
                self.assertFalse(d.executed)

    def test_never_mistake_planning_for_execution(self):
        for operation in ("control", "receipt", "bulk"):
            for free in (0, 4096*MIB):
                self.assertFalse(self.call(free, operation).executed)

    def test_bool_or_float_memory_rejected(self):
        for value in (True, False, 4.0, "100", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    plan_operation(total_bytes=4096*MIB, available_bytes=value,
                                   operation="control")

    def test_negative_excessive_and_zero_total_rejected(self):
        for total, free in ((0, 0), (1, -1), (100, 101)):
            with self.assertRaises(ValueError):
                plan_operation(total_bytes=total, available_bytes=free,
                               operation="control")

    def test_unknown_operation_fails_closed(self):
        for operation in ("", "delete", "install", None, 7):
            with self.assertRaises(ValueError):
                self.call(128*MIB, operation=operation)

    def test_permitted_operations_no_hidden_allocation(self):
        for operation in ("control", "receipt"):
            self.assertEqual(self.call(1, operation).chunk_bytes, 0)


if __name__ == "__main__":
    unittest.main()
