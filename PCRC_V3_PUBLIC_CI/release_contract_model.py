"""Pure public safety contract: no signing, no keys, no Windows actions."""
import re

def _sha(value):
    return type(value) is str and re.fullmatch("[0-9a-f]{64}", value) is not None

def check_release(record, *, expected_source_sha, official_signature_verified,
                  trusted_authority_verified):
    hold = lambda why: {"state": "HOLD_" + why, "install_allowed": False}
    if type(record) is not dict:
        return hold("BAD_RECORD")
    if record.get("schema") != "PCRC-PUBLIC-SYNTHETIC-1":
        return hold("BAD_SCHEMA")
    source = record.get("source_sha256")
    package = record.get("archive_sha256")
    if not _sha(source) or not _sha(package) or not _sha(expected_source_sha):
        return hold("BAD_HASH_FORMAT")
    if source != expected_source_sha:
        return hold("SOURCE_PIN_MISMATCH")
    if official_signature_verified is not True or trusted_authority_verified is not True:
        return hold("UNVERIFIED_SIGNER")
    if record.get("manifest_member_hashes_verified") is not True:
        return hold("UNVERIFIED_MEMBERS")
    if record.get("tamper_rejected") is not True:
        return hold("TAMPER_GATE")
    if record.get("rollback_code_only") is not True:
        return hold("ROLLBACK_GATE")
    if record.get("current_db_preserved") is not True:
        return hold("CURRENT_DB_GATE")
    if record.get("owner_grant_valid") is not True or record.get("replay_rejected") is not True:
        return hold("OWNER_AND_REPLAY_GATE")
    if record.get("production_mutated") is not False:
        return hold("PRODUCTION_ISOLATION")
    return {"state": "CONTRACT_MODEL_PASS", "install_allowed": False,
            "official_deployment_attested": False}
