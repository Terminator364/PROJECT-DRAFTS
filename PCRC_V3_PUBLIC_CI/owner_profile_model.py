"""Public synthetic Windows owner-profile contract. No private PCRC source."""
import ntpath

def _canon(path):
    if not isinstance(path, str) or not path or not ntpath.isabs(path):
        return ""
    norm = path.replace("/", "\\")
    if ".." in norm.split("\\"):
        return ""
    return ntpath.normcase(ntpath.normpath(norm))

def check_owner(snapshot, expected_identity):
    required = ("identity", "sid", "registry_profile", "userprofile", "python_home")
    if not isinstance(snapshot, dict) or any(not isinstance(snapshot.get(k), str) or
                                               not snapshot[k] for k in required):
        return {"state": "HOLD_MISSING_IDENTITY", "installation_allowed": False}
    if snapshot["identity"].casefold() != expected_identity.casefold():
        return {"state": "HOLD_OWNER_MISMATCH", "installation_allowed": False}
    trusted = _canon(snapshot["registry_profile"])
    actual = _canon(snapshot["userprofile"])
    home = _canon(snapshot["python_home"])
    if not trusted or not actual or not home:
        return {"state": "HOLD_INVALID_PROFILE", "installation_allowed": False}
    if trusted != actual or trusted != home:
        return {"state": "HOLD_NONCANONICAL_PROFILE", "installation_allowed": False}
    if snapshot.get("trusted_root_exists") is not True:
        return {"state": "HOLD_ROOT_MISSING", "installation_allowed": False}
    if snapshot.get("public_anchor_exists") is not True:
        return {"state": "HOLD_TRUST_ANCHOR_MISSING", "installation_allowed": False}
    return {"state": "PROFILE_MATCHES_READONLY", "installation_allowed": False}
