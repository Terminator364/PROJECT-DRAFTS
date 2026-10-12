"""Deterministic non-hardware rescue-bridge simulator. No real PC commands are executed."""
from __future__ import annotations
from dataclasses import dataclass
import copy
import hashlib
import hmac
import json

DEMO_KEY = b"SIMULATION_ONLY_NOT_A_PRODUCTION_SECRET"
READ_ACTIONS = frozenset({"ping", "health", "list_files", "read_file", "logs"})
MUTATING_ACTIONS = frozenset({"write_file", "restart_agent"})
ACTIONS = READ_ACTIONS | MUTATING_ACTIONS

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

@dataclass
class Conditions:
    phone_internet: bool = True
    pc_internet: bool = True
    phone_awake: bool = True
    pc_awake: bool = True
    cable_plugged: bool = True
    usb_network_enabled: bool = True
    device_paired: bool = True
    pc_agent_running: bool = True
    supervisor_running: bool = True
    phone_battery_pct: int = 70

class RescueLab:
    """Models ChatGPT -> cloud -> Android -> USB -> Windows agent.
    Cloud reachability of the PC is intentionally NOT required.
    Each envelope is device-bound, MAC-authenticated and replay-protected.
    """
    def __init__(self, conditions=None, *, key=DEMO_KEY, target="MBMPC"):
        self.conditions = copy.deepcopy(conditions or Conditions())
        self.key = key
        self.target = target
        self.next_seq = 0
        self.seen = set()
        self.pending = []
        self.audit = []
        self.files = {"/lab/hello.txt": "Virtual Windows sandbox. No physical files touched."}

    def sign(self, envelope):
        msg = canonical(envelope).encode("utf-8")
        return hmac.new(self.key, msg, hashlib.sha256).hexdigest()

    def packet(self, action, payload=None, approved=False, *, target=None):
        self.next_seq += 1
        e = {"target": target or self.target, "sequence": self.next_seq,
             "action": action, "payload": payload or {}, "approved": bool(approved)}
        return {"envelope": e, "mac": self.sign(e)}

    def submit(self, action, payload=None, approved=False, *, target=None):
        p = self.packet(action, payload, approved, target=target)
        if self.pending:
            self.pending.append(p)
            return self._receipt("QUEUED", "OLDER_TASKS_PENDING", p)
        state = self._reachability()
        if state:
            self.pending.append(p)
            return self._receipt("QUEUED", state, p)
        return self.deliver(p)

    def _reachability(self):
        c = self.conditions
        if not c.phone_internet: return "PHONE_CLOUD_OFFLINE"
        if not c.phone_awake: return "PHONE_ASLEEP"
        if c.phone_battery_pct <= 2: return "PHONE_BATTERY_CRITICAL"
        if not c.cable_plugged: return "USB_CABLE_UNPLUGGED"
        if not c.usb_network_enabled: return "USB_DATA_UNAVAILABLE"
        if not c.pc_awake: return "PC_ASLEEP"
        return ""

    def _receipt(self, status, code, packet, *, value=None):
        e = packet.get("envelope", {})
        receipt = {"status": status, "reason": code,
                   "sequence": e.get("sequence"), "action": e.get("action"),
                   "target": e.get("target")}
        if value is not None: receipt["value"] = value
        self.audit.append(receipt)
        return receipt

    def deliver(self, packet):
        """Public test seam: malformed signatures and replay can be injected."""
        e = packet.get("envelope")
        if not isinstance(e, dict):
            return self._receipt("REJECTED", "INVALID_ENVELOPE", packet)
        if e.get("target") != self.target:
            return self._receipt("REJECTED", "DEVICE_IDENTITY_MISMATCH", packet)
        if not hmac.compare_digest(str(packet.get("mac", "")), self.sign(e)):
            return self._receipt("REJECTED", "BAD_SIGNATURE", packet)
        seq = e.get("sequence")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
            return self._receipt("REJECTED", "BAD_SEQUENCE", packet)
        if seq in self.seen:
            return self._receipt("REJECTED", "REPLAY", packet)
        if not self.conditions.device_paired:
            return self._receipt("REJECTED", "NOT_PAIRED", packet)
        if self._reachability():
            return self._receipt("UNAVAILABLE", self._reachability(), packet)
        self.seen.add(seq)
        action = e.get("action")
        if action not in ACTIONS:
            return self._receipt("REJECTED", "ACTION_NOT_ALLOWED", packet)
        if action in MUTATING_ACTIONS and e.get("approved") is not True:
            return self._receipt("REJECTED", "LOCAL_APPROVAL_REQUIRED", packet)
        if action == "restart_agent":
            if not self.conditions.supervisor_running:
                return self._receipt("FAILED", "SUPERVISOR_DOWN", packet)
            self.conditions.pc_agent_running = True
            return self._receipt("SUCCESS", "SUPERVISOR_RECOVERY_SIMULATED", packet)
        if not self.conditions.pc_agent_running:
            return self._receipt("UNAVAILABLE", "PC_AGENT_DOWN", packet)
        if action in ("ping", "health"):
            value = {"pc": self.target, "agent": "RUNNING", "usb": "LINKED",
                     "pc_internet": self.conditions.pc_internet}
            return self._receipt("SUCCESS", "VIRTUAL_AGENT_RESPONSE", packet, value=value)
        if action == "logs":
            return self._receipt("SUCCESS", "SIMULATED_LOGS", packet,
                                 value={"entries": len(self.audit)})
        path = e.get("payload", {}).get("path", "")
        if action == "list_files":
            return self._receipt("SUCCESS", "VIRTUAL_FILES", packet,
                                 value=sorted(self.files))
        if not isinstance(path, str) or not path.startswith("/lab/") or ".." in path.split("/"):
            return self._receipt("REJECTED", "SANDBOX_PATH_REQUIRED", packet)
        if action == "read_file":
            if path not in self.files:
                return self._receipt("FAILED", "NO_SUCH_VIRTUAL_FILE", packet)
            return self._receipt("SUCCESS", "VIRTUAL_READ", packet,
                                 value=self.files[path])
        if action == "write_file":
            content = e.get("payload", {}).get("content")
            if not isinstance(content, str) or len(content.encode("utf-8")) > 64000:
                return self._receipt("REJECTED", "INVALID_CONTENT_OR_TOO_LARGE", packet)
            self.files[path] = content
            return self._receipt("SUCCESS", "VIRTUAL_WRITE", packet,
                                 value={"bytes": len(content.encode("utf-8"))})
        return self._receipt("REJECTED", "ACTION_NOT_IMPLEMENTED", packet)

    def flush(self):
        results = []
        while self.pending and not self._reachability():
            p = self.pending.pop(0)
            results.append(self.deliver(p))
        return results

def run_scenarios():
    """Independent test fixtures; none connect to the actual phone or PC."""
    out = {}
    def check(name, setup=None, action="health", payload=None, approved=False):
        lab = RescueLab(setup)
        out[name] = lab.submit(action, payload, approved)
    check("normal_usb")
    check("pc_cloud_offline_usb_still_works", Conditions(pc_internet=False))
    check("cable_removed", Conditions(cable_plugged=False))
    check("charge_only", Conditions(usb_network_enabled=False))
    check("phone_offline", Conditions(phone_internet=False))
    check("phone_asleep", Conditions(phone_awake=False))
    check("pc_asleep", Conditions(pc_awake=False))
    check("pc_agent_crashed", Conditions(pc_agent_running=False))
    check("guardian_repairs_agent", Conditions(pc_agent_running=False),
          "restart_agent", approved=True)
    check("supervisor_down", Conditions(pc_agent_running=False, supervisor_running=False),
          "restart_agent", approved=True)
    check("unpaired_phone", Conditions(device_paired=False))
    check("mutation_requires_approval", action="write_file",
          payload={"path":"/lab/notes.txt","content":"test"})
    check("approved_sandbox_write", action="write_file",
          payload={"path":"/lab/notes.txt","content":"test"}, approved=True)
    check("sandbox_escape", action="read_file", payload={"path":"/lab/../secrets.txt"})
    check("battery_critical", Conditions(phone_battery_pct=1))
    lab = RescueLab(Conditions(phone_internet=False))
    first = lab.submit("health")
    lab.conditions.phone_internet = True
    follow = lab.flush()
    out["offline_queue_then_resume"] = {"queued": first, "flushed": follow}
    lab = RescueLab()
    packet = lab.packet("health")
    out["valid_packet"] = lab.deliver(packet)
    out["replay_rejected"] = lab.deliver(packet)
    pkt = lab.packet("health")
    pkt["mac"] = "0"*64
    out["tamper_rejected"] = lab.deliver(pkt)
    out["wrong_device_rejected"] = lab.deliver(lab.packet("health", target="OTHER"))
    return out

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Virtual phone/USB/Windows rescue lab.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = run_scenarios()
    print(json.dumps(results, indent=2, ensure_ascii=False) if args.json else
          "\n".join(f"{name}: {v['status'] if 'status' in v else 'QUEUE_RESUMED'}" for name, v in results.items()))
