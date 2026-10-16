#!/usr/bin/env python3
"""GitHub Actions public-source fail-closed inventory/hash/privacy gate."""
import hashlib, json, pathlib, re
root=pathlib.Path(__file__).resolve().parents[1]
manifest=json.loads((root/"ci-migration/public-source-manifest.json").read_text(encoding="utf-8"))
expected={s["path"]:s["git_blob_sha1"] for s in manifest["files"]}
actual={p.relative_to(root).as_posix() for sub in ("tools/dc_oneclick_qa","tests/dc_oneclick_qa") for p in (root/sub).rglob("*") if p.is_file()}
if actual != set(expected):
    raise SystemExit("PUBLIC_MIRROR_INVENTORY_DRIFT missing="+repr(sorted(set(expected)-actual))+" extra="+repr(sorted(actual-set(expected))))
sensitive=re.compile(rb"ghp_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:blessing|mabongo|Terminator364)|192\.168\.\d+\.\d+",re.I)
for path,expected_hash in expected.items():
    content=(root/path).read_bytes()
    computed=hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
    if computed != expected_hash:
        raise SystemExit("PUBLIC_MIRROR_HASH_DRIFT="+path)
    if sensitive.search(content):
        raise SystemExit("PUBLIC_MIRROR_PRIVATE_MARKER="+path)
print("PUBLIC_MIRROR_POLICY_PASS",len(expected),"files")
