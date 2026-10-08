#!/usr/bin/env python3
"""Read-only gate for migration manifests. No network or destructive operations."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

HASH = re.compile(r"^[a-f0-9]{64}$")
DANGEROUS = {"DELETE", "MOVE", "OVERWRITE"}
PROTECTED = {"ACTIVE", "GOVERNANCE", "WORKER", "LIVE", "CHECKPOINT", "ROLLBACK"}

def valid_path(path: str, root: str) -> bool:
    p = path.replace("\\", "/").rstrip("/")
    r = root.replace("\\", "/").rstrip("/")
    if not r or not p.startswith(r + "/"):
        return False
    rel = p[len(r) + 1:].split("/")
    return all(part not in ("", ".", "..") for part in rel)

def hash_verified_record(item: dict[str, Any]) -> bool:
    """Compute SHA-256 of the *actual* readable local bytes, never trust flags alone."""
    expected = str(item.get("sha256", "")).lower()
    local_file = item.get("local_file")
    if not HASH.fullmatch(expected) or not isinstance(local_file, str) or not local_file:
        return False
    try:
        path = Path(local_file)
        if not path.is_file():
            return False
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest() == expected
    except (OSError, ValueError):
        return False


def audit(manifest: dict[str, Any]) -> dict[str, Any]:
    """Fail closed on ambiguous migrations, shadow duplicates, or missing bytes."""
    root = str(manifest.get("canonical_root", "")).strip()
    records = manifest.get("items", [])
    failures: list[str] = []
    if not isinstance(records, list):
        return {"ok": False, "failures": ["items must be an array"], "items_checked": 0}
    by_id: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(records):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            failures.append(f"row {i}: non-blank string id required")
            continue
        if item["id"] in by_id:
            failures.append(f"duplicate identity: {item['id']}")
        by_id[item["id"]] = item
    for i, item in enumerate(records):
        if not isinstance(item, dict) or not item.get("id"):
            continue
        item_id = item["id"]
        action = str(item.get("action", "PRESERVE")).upper()
        role = str(item.get("role", "UNKNOWN")).upper()
        deps = item.get("dependencies", [])
        if not isinstance(deps, list):
            failures.append(f"{item_id}: dependencies must be an array")
            deps = ["UNKNOWN"]
        if action not in {"PRESERVE", "REFERENCE", "MOVE", "DELETE", "OVERWRITE"}:
            failures.append(f"{item_id}: invalid action {action}")
        if action in DANGEROUS and (any(role == r or role.startswith(r + "_") for r in PROTECTED) or item.get("active", False)):
            failures.append(f"{item_id}: active/protected item cannot be mutated")
        if action == "MOVE":
            dest = str(item.get("target_path", ""))
            if not valid_path(dest, root):
                failures.append(f"{item_id}: target is outside canonical root or unsafe")
            if not item.get("readback_id_match", False):
                failures.append(f"{item_id}: ID-preserving readback not proven")
            if item.get("absolute_path_reference") or deps:
                failures.append(f"{item_id}: unresolved path or external dependencies")
        if action == "DELETE":
            survivor_id = item.get("survivor_id")
            survivor = by_id.get(survivor_id)
            ownhash = str(item.get("sha256", "")).lower()
            if not survivor or survivor_id == item_id:
                failures.append(f"{item_id}: independent survivor unavailable")
            elif survivor.get("action", "PRESERVE").upper() == "DELETE":
                failures.append(f"{item_id}: survivor is also scheduled for deletion")
            if not HASH.fullmatch(ownhash) or not hash_verified_record(item):
                failures.append(f"{item_id}: verified SHA-256 of source missing")
            if not survivor or str(survivor.get("sha256", "")).lower() != ownhash or not hash_verified_record(survivor):
                failures.append(f"{item_id}: byte-identical survivor not verified")
            if deps or item.get("absolute_path_reference") or not item.get("reference_scan_complete"):
                failures.append(f"{item_id}: cannot delete without dependency-scan clearance")
        if action == "OVERWRITE":
            failures.append(f"{item_id}: overwrite forbidden in dry-run migration")
    return {"ok": not failures, "items_checked": len(records), "failures": failures,
            "actions": {a: sum(str(x.get("action", "PRESERVE")).upper() == a for x in records if isinstance(x, dict))
                        for a in ["PRESERVE", "REFERENCE", "MOVE", "DELETE", "OVERWRITE"]}}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="local JSON manifest; never send raw data to public Git")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = audit(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
