"""Portable low-memory scheduling policy. No I/O, state, secrets or services.

The policy does not reserve RAM or execute work. Callers must durably enqueue
deferred operations before confirming acceptance, and must separately monitor
memory during execution. A decision is never proof of operational success.
"""
from __future__ import annotations

from dataclasses import dataclass

MIB = 1024 * 1024
BULK_HEADROOM_BYTES = 128 * MIB
MAX_BULK_CHUNK_BYTES = 64 * 1024
VALID_OPERATIONS = frozenset({"control", "receipt", "bulk"})


@dataclass(frozen=True)
class ResourceDecision:
    operation: str
    action: str
    chunk_bytes: int
    memory_used_percent: int
    reason: str

    @property
    def action_requires_durable_queue(self) -> bool:
        return self.action == "DEFER_HEAVY"

    @property
    def executed(self) -> bool:
        # These are *planning* decisions; the caller must verify effects.
        return False


def plan_operation(*, total_bytes: int, available_bytes: int,
                   operation: str) -> ResourceDecision:
    """Always attempt minimal control/receipt work, defer memory-hungry tasks.

    99%-used RAM is not a blanket admission rejection; 0 free bytes also
    cannot imply Windows will physically honor an allocation.
    """
    if (type(total_bytes) is not int or type(available_bytes) is not int
            or total_bytes <= 0 or available_bytes < 0
            or available_bytes > total_bytes):
        raise ValueError("invalid physical memory measurement")
    if type(operation) is not str or operation not in VALID_OPERATIONS:
        raise ValueError("unknown task class")
    used_percent = ((total_bytes - available_bytes) * 100) // total_bytes
    if operation in {"control", "receipt"}:
        return ResourceDecision(
            operation, "ATTEMPT_LIGHTWEIGHT", 0, used_percent,
            "bounded request path, real execution still unverified")
    if available_bytes < BULK_HEADROOM_BYTES:
        return ResourceDecision(
            operation, "DEFER_HEAVY", 0, used_percent,
            "heavy operation requires durable queue and later retry")
    chunk = min(MAX_BULK_CHUNK_BYTES, max(4096, available_bytes // 1024))
    return ResourceDecision(
        operation, "ALLOW_CHUNKED", chunk, used_percent,
        "stream in bounded chunks, recheck memory on each frame")
