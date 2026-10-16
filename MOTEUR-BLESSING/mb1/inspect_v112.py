#!/usr/bin/env python3
"""Moteur Blessing MB-1: inventaire V1.1.2 en lecture seule, sans scoring.

Python standard library only. An archive is accepted for structural inspection
ONLY after exact receipt SHA-256, size, ZIP CRC and path-safety checks.
This does not establish scientific, PIT or sport-prediction validity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile

RECEIPT_SHA256 = "5ef731d6ee4b5edb8a741c59a565d4f7363be84eb9225e814345cb0a04fe89e0"
RECEIPT_BYTES = 12_241_975
MAX_ITEMS = 1000
MAX_UNCOMPRESSED_BYTES = 500 * 1024 * 1024
MAX_JSON_BYTES = 25 * 1024 * 1024
REQUIRED = (
    "00_LIRE_EN_PREMIER.md",
    "01_AUDIT_CINQ_CYCLES.md",
    "02_REPRISE_COLLAB_MATRICE.md",
    "config/RECETTES_62_EXECUTABLES.json",
    "config/REGISTRE_372_RECETTES_ACQUISITION_V112.json",
    "config/ETAT_REEL_62_MONDES_V112.csv",
    "code/moteur_v112.py",
    "tests_v112/test_v112.py",
)


class AuditError(Exception):
    """Reject structurally unsafe or unauthenticated input."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def safe_members(zf: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    infos = zf.infolist()
    if not infos or len(infos) > MAX_ITEMS:
        raise AuditError("ZIP vide ou nombre d'entrees hors limite")
    seen: set[str] = set()
    out: dict[str, zipfile.ZipInfo] = {}
    total = 0
    for item in infos:
        raw = item.filename
        if not raw or "\\" in raw or "\x00" in raw:
            raise AuditError("Chemin ZIP non conforme")
        pure = PurePosixPath(raw)
        if (raw.startswith("/") or ":" in raw.split("/")[0] or
            any(part in (".", "..") for part in raw.split("/"))):
            raise AuditError("Chemin ZIP absolu, ambigu ou traversant")
        normalized = str(pure).rstrip("/")
        if normalized in seen:
            raise AuditError("Chemins ZIP dupliques")
        seen.add(normalized)
        unix_mode = item.external_attr >> 16
        if stat.S_IFMT(unix_mode) == stat.S_IFLNK:
            raise AuditError("Lien symbolique interdit")
        if item.flag_bits & 1:
            raise AuditError("Entree ZIP chiffree")
        total += item.file_size
        if item.file_size > MAX_JSON_BYTES and raw.endswith(".json"):
            raise AuditError("JSON trop volumineux")
        if total > MAX_UNCOMPRESSED_BYTES:
            raise AuditError("Expansion ZIP au-dela du plafond")
        if not item.is_dir():
            out[normalized] = item
    failed = zf.testzip()
    if failed is not None:
        raise AuditError("Echec CRC ZIP : " + failed)
    return out


def json_profile(zf: zipfile.ZipFile, item: zipfile.ZipInfo) -> dict:
    with zf.open(item, "r") as fh:
        raw = fh.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise AuditError("JSON depasse la limite lecture")
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"JSON invalide ({item.filename}): {exc}") from exc
    result = {"root_type": type(data).__name__}
    if isinstance(data, list):
        result["root_items"] = len(data)
    elif isinstance(data, dict):
        result["top_level_keys"] = sorted(data.keys())
        result["top_level_arrays"] = {
            key: len(value) for key, value in data.items() if isinstance(value, list)
        }
        result["top_level_objects"] = {
            key: len(value) for key, value in data.items() if isinstance(value, dict)
        }
    return result


def inspect(path: Path, expected_sha: str = RECEIPT_SHA256,
            expected_size: int = RECEIPT_BYTES) -> dict:
    if not path.is_file():
        raise AuditError("Archive absente")
    size = path.stat().st_size
    if size != expected_size:
        raise AuditError(f"Taille invalide: {size} != {expected_size}")
    sha = sha256_file(path)
    if sha.lower() != expected_sha.lower():
        raise AuditError("SHA256 divergent: archive refusee")
    try:
        with zipfile.ZipFile(path, "r") as zf:
            members = safe_members(zf)
            missing = [name for name in REQUIRED if name not in members]
            profiles = {}
            for name in REQUIRED:
                if name in members and name.endswith(".json"):
                    profiles[name] = json_profile(zf, members[name])
            return {
                "schema": "moteur-blessing/mb1/structural-inspection/v1",
                "input_name": path.name,
                "receipt_sha256_verified": True,
                "receipt_bytes_verified": True,
                "zip_crc_verified": True,
                "zip_paths_safe": True,
                "members": len(members),
                "required_present": len(REQUIRED) - len(missing),
                "required_total": len(REQUIRED),
                "missing": missing,
                "json_profiles": profiles,
                "structure_status": "COMPLETE" if not missing else "INCOMPLETE",
                "actual_62_240_140_372_mappings_validated": False,
                "PIT_sources_validated": False,
                "sporting_performance_validated": False,
                "score_activation_allowed": False,
                "next_step": "Inspecter les schemas et mapper les 372 vrais enregistrements; ne pas inferer leurs champs",
            }
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        raise AuditError(f"Archive ZIP illisible: {exc}") from exc


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--output", type=Path, help="Rapport JSON, nouveau fichier seulement")
    args = p.parse_args(argv)
    try:
        report = inspect(args.archive)
        serialized = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(serialized + "\n")
        print(serialized)
        return 0 if report["structure_status"] == "COMPLETE" else 2
    except (AuditError, FileExistsError) as exc:
        print(f"MB1_REJECTED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
