"""Public, synthetic PCRC V2 resilience contract model. No private source code."""
from dataclasses import dataclass

MAX_CHUNK_BYTES = 256 * 1024
MIN_CHUNK_BYTES = 4 * 1024


@dataclass(frozen=True)
class Decision:
    action: str
    chunk_bytes: int
    reason: str


def decide_operation(*, available_bytes: int, operation: str) -> Decision:
    """Keep lightweight control responsive, and defer bulk work when memory is tight.

    Synthetic policy, not a measurement or certification of the private Core.
    """
    if available_bytes < 0:
        raise ValueError("available_bytes must be nonnegative")
    if operation not in {"control", "journal", "bulk"}:
        raise ValueError("unknown operation")
    if operation in {"control", "journal"}:
        return Decision("ACCEPT_LIGHTWEIGHT", 0, "bounded control path")
    if available_bytes < 8 * 1024 * 1024:
        return Decision("DEFER_PERSISTENTLY", 0, "memory pressure")
    chunk = max(MIN_CHUNK_BYTES, min(MAX_CHUNK_BYTES, available_bytes // 64))
    return Decision("STREAM_BOUNDED", chunk, "bounded chunks")


def validate_public_payload(payload: dict) -> None:
    """Reject production identifiers and accidental binary/data disclosures."""
    permitted = {"case_id", "operation", "available_bytes", "expected_action"}
    if not isinstance(payload, dict) or set(payload) != permitted:
        raise ValueError("unexpected fields")
    if not isinstance(payload["case_id"], str) or not payload["case_id"].isascii() or len(payload["case_id"]) > 64:
        raise ValueError("unsafe case identifier")
    if payload["operation"] not in {"control", "journal", "bulk"}:
        raise ValueError("unsafe operation")
    if type(payload["available_bytes"]) is not int or payload["available_bytes"] < 0:
        raise ValueError("unsafe capacity")
    if payload["expected_action"] not in {"ACCEPT_LIGHTWEIGHT", "DEFER_PERSISTENTLY", "STREAM_BOUNDED"}:
        raise ValueError("unsafe expectation")
