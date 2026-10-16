"""Testable safety contract for Desktop Commander one-click reconnect.
No side effects: selection and control-plane policy only. NEVER kills a process.
The production field script still requires an integration gate.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Proc:
    pid: int
    ppid: int
    name: str
    cmd: str

def _remote_entry(proc: Proc) -> bool:
    name, cmd = proc.name.casefold(), proc.cmd.casefold()
    # Narrow identifiers: never select a generic Node.js or Python server.
    return (
        name == "cmd.exe"
        and ("npx.cmd" in cmd and "@wonderwhy-er/desktop-commander" in cmd and " remote" in cmd)
    ) or (
        name == "node.exe"
        and ("@wonderwhy-er" in cmd and "desktop-commander" in cmd and "index.js" in cmd and " remote" in cmd)
    )

def remote_roots(all_processes: Iterable[Proc]) -> list[int]:
    processes = {p.pid: p for p in all_processes}
    candidates = {p.pid for p in processes.values() if _remote_entry(p)}
    roots = []
    for pid in sorted(candidates):
        seen = {pid}
        parent = processes[pid].ppid
        descended = False
        while parent in processes and parent not in seen:
            if parent in candidates:
                descended = True
                break
            seen.add(parent)
            parent = processes[parent].ppid
        if not descended:
            roots.append(pid)
    return roots

@dataclass(frozen=True)
class Plan:
    operation: str
    roots: tuple[int, ...]
    reason: str
    # Must not assert cloud connectivity from local process inventory.
    cloud_online_verified: bool = False

def propose(processes: Iterable[Proc], *, cloud_status: str, user_clicked: bool) -> Plan:
    """Cloud status is verified by an authenticated remote probe, never guessed.
    Unknown must not automatically kill the last functioning remote connection.
    """
    roots = tuple(remote_roots(processes))
    if not user_clicked:
        return Plan("NOOP", roots, "No user-triggered reconnect")
    if cloud_status not in {"ONLINE", "OFFLINE", "UNKNOWN"}:
        raise ValueError("Invalid cloud status")
    if cloud_status == "ONLINE":
        return Plan("REVEAL_EXISTING", roots, "Current remote is verified online", True)
    if cloud_status == "UNKNOWN" and roots:
        return Plan("PRESERVE_AND_DIAGNOSE", roots, "Avoid destroying last unverified channel")
    if cloud_status == "OFFLINE" and roots:
        return Plan("RESTART_AFTER_PREPARE", roots, "Prepare independent launcher, then stop only target")
    return Plan("START_EMERGENCY_CMD", roots, "No remote root present")
