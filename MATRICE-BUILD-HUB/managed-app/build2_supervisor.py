from __future__ import annotations

import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from build2_core import (
    GLOBAL, LOCK, BUILD2_VERSION, atomic_json, lane_root, read_json,
    utc, write_receipt
)

SUPERVISOR_PID = GLOBAL / "supervisor.pid.json"
SCHEDULER_PID = GLOBAL / "scheduler.pid.json"
SUPERVISOR_HEARTBEAT = GLOBAL / "supervisor.heartbeat.json"
SUPERVISOR_EXIT = GLOBAL / "supervisor.last_exit.json"
SUPERVISOR_LAUNCH = GLOBAL / "supervisor.last_launch.json"
SUPERVISOR_LOG = GLOBAL / "supervisor.log"

NTSTATUS_CTRL_C_EXIT = 0xC000013A
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9

class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", ctypes.c_uint32),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_uint32),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_uint32),
        ("SchedulingClass", ctypes.c_uint32),
    ]

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]

class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]

def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False

def _current_process_in_job() -> bool:
    if os.name != "nt":
        return False
    flag = ctypes.c_int(0)
    kernel32 = ctypes.windll.kernel32
    ok = kernel32.IsProcessInJob(kernel32.GetCurrentProcess(), None, ctypes.byref(flag))
    return bool(ok and flag.value)

def _write_heartbeat(status: str, detail: str = "", *, scheduler_pid: int | None = None) -> None:
    atomic_json(SUPERVISOR_HEARTBEAT, {
        "schema": "build2.supervisor_heartbeat/1",
        "build2_version": BUILD2_VERSION,
        "status": status,
        "timestamp_utc": utc(),
        "supervisor_pid": os.getpid(),
        "scheduler_pid": scheduler_pid,
        "detail": detail,
    })

def _exit_class(rc: int) -> tuple[str, str]:
    raw = int(rc) & 0xFFFFFFFF
    hx = f"0x{raw:08X}"
    if raw == NTSTATUS_CTRL_C_EXIT:
        return "EXTERNAL_TERMINATION_CTRL_EVENT", hx
    if raw >= 0xC0000000:
        return "EXTERNAL_TERMINATION_NTSTATUS", hx
    return "SUPERVISOR_CHILD_EXIT_NONZERO", hx

def _active_run() -> tuple[str | None, str | None]:
    cur = read_json(LOCK, {}) or {}
    return cur.get("project"), cur.get("run_id")

def _open_kill_job_for_process(proc: subprocess.Popen) -> int | None:
    if os.name != "nt":
        return None
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateJobObjectW.restype = ctypes.c_void_p
    kernel32.OpenProcess.restype = ctypes.c_void_p
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return None
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    ok = kernel32.SetInformationJobObject(
        ctypes.c_void_p(job),
        JobObjectExtendedLimitInformation,
        ctypes.byref(info),
        ctypes.sizeof(info),
    )
    if not ok:
        kernel32.CloseHandle(ctypes.c_void_p(job))
        return None
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_TERMINATE = 0x0001
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = kernel32.OpenProcess(
        PROCESS_SET_QUOTA | PROCESS_TERMINATE | PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        int(proc.pid),
    )
    if not handle:
        kernel32.CloseHandle(ctypes.c_void_p(job))
        return None
    try:
        ok = kernel32.AssignProcessToJobObject(ctypes.c_void_p(job), ctypes.c_void_p(handle))
    finally:
        kernel32.CloseHandle(ctypes.c_void_p(handle))
    if not ok:
        kernel32.CloseHandle(ctypes.c_void_p(job))
        return None
    return int(job)

def _close_handle(handle: int | None) -> None:
    if os.name == "nt" and handle:
        ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(handle))

def monitor(worker_path: str) -> int:
    GLOBAL.mkdir(parents=True, exist_ok=True)
    atomic_json(SUPERVISOR_PID, {
        "pid": os.getpid(),
        "started_at": utc(),
        "build2_version": BUILD2_VERSION,
    })
    gate = GLOBAL / f"scheduler-gate-{os.getpid()}.ready"
    try:
        gate.unlink()
    except FileNotFoundError:
        pass

    try:
        with SUPERVISOR_LOG.open("a", encoding="utf-8", errors="replace") as lf:
            proc = subprocess.Popen(
                [sys.executable, str(Path(worker_path).resolve()), "scheduler", str(gate)],
                stdin=subprocess.DEVNULL,
                stdout=lf,
                stderr=subprocess.STDOUT,
                cwd=str(Path(worker_path).resolve().parent),
                shell=False,
                close_fds=True,
                creationflags=((getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)) if os.name == "nt" else 0),
            )
            job_handle = _open_kill_job_for_process(proc)
            atomic_json(SCHEDULER_PID, {
                "pid": proc.pid,
                "supervisor_pid": os.getpid(),
                "started_at": utc(),
                "build2_version": BUILD2_VERSION,
                "job_object": bool(job_handle),
            })
            gate.write_text("GO\n", encoding="ascii")
            _write_heartbeat("RUNNING", "scheduler started", scheduler_pid=proc.pid)

            while proc.poll() is None:
                _write_heartbeat("RUNNING", "scheduler alive", scheduler_pid=proc.pid)
                time.sleep(2)

            rc = int(proc.returncode or 0)
            err_class, hx = _exit_class(rc) if rc != 0 else (None, "0x00000000")
            payload = {
                "schema": "build2.supervisor_exit/1",
                "build2_version": BUILD2_VERSION,
                "timestamp_utc": utc(),
                "supervisor_pid": os.getpid(),
                "scheduler_pid": proc.pid,
                "return_code": rc,
                "return_code_unsigned": rc & 0xFFFFFFFF,
                "return_code_hex": hx,
                "error_class": err_class,
                "job_object": bool(job_handle),
            }
            atomic_json(SUPERVISOR_EXIT, payload)

            if rc != 0:
                project, run_id = _active_run()
                if project and run_id:
                    lane = lane_root(str(project))
                    st = read_json(lane / "runs" / str(run_id) / "state.json", {}) or {}
                    stage = str(st.get("stage") or "ACCEPTED")
                    write_receipt(
                        str(project),
                        str(run_id),
                        "FAILED_SAFE",
                        stage=stage,
                        error_class=err_class,
                        evidence=[{
                            "kind": "supervisor_child_exit",
                            "return_code": rc,
                            "return_code_unsigned": rc & 0xFFFFFFFF,
                            "return_code_hex": hx,
                            "job_object": bool(job_handle),
                            "log": str(SUPERVISOR_LOG),
                        }],
                        detail=f"Scheduler exited abnormally with {hx}; see supervisor log.",
                    )
            _write_heartbeat("COMPLETE" if rc == 0 else "FAILED_SAFE", f"scheduler exit {hx}", scheduler_pid=proc.pid)
            _close_handle(job_handle)
            return rc
    finally:
        try:
            gate.unlink()
        except FileNotFoundError:
            pass

def _write_bootstrap(worker_path: str) -> Path:
    GLOBAL.mkdir(parents=True, exist_ok=True)
    path = GLOBAL / "launch-supervisor.cmd"
    def esc(value: str) -> str:
        if "\n" in value or "\r" in value or '"' in value:
            raise RuntimeError("UNSAFE_SUPERVISOR_ENV")
        return value.replace("%", "%%")
    lines = ["@echo off", "setlocal"]
    lines.append(f'set "LOCALAPPDATA={esc(str(os.environ.get("LOCALAPPDATA") or ""))}"')
    control = str(os.environ.get("PCA_CONTROL_FOLDER") or "")
    if control:
        lines.append(f'set "PCA_CONTROL_FOLDER={esc(control)}"')
    lines.append(
        '"' + esc(sys.executable) + '" "' + esc(str(Path(__file__).resolve())) +
        '" monitor "' + esc(str(Path(worker_path).resolve())) + '"'
    )
    lines.append("exit /b %errorlevel%")
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    return path

def _spawn_via_cim(worker_path: str) -> dict:
    bootstrap = _write_bootstrap(worker_path)
    comspec = os.environ.get("COMSPEC") or str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe")
    cmdline = f'"{comspec}" /d /s /c ""{bootstrap}""'
    env = os.environ.copy()
    env["MBH_WMI_CMDLINE"] = cmdline
    ps = str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe")
    script = (
        "$ErrorActionPreference='Stop';"
        "$r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
        "-Arguments @{CommandLine=$env:MBH_WMI_CMDLINE};"
        "if([int]$r.ReturnValue -ne 0){exit [int]$r.ReturnValue};"
        "[Console]::Out.Write([string]$r.ProcessId)"
    )
    cp = subprocess.run(
        [ps, "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, shell=False, timeout=25, env=env
    )
    if cp.returncode != 0 or not cp.stdout.strip().isdigit():
        raise RuntimeError("CIM_SUPERVISOR_LAUNCH_FAILED:" + (cp.stderr or cp.stdout)[-1000:])
    return {"status": "STARTED", "pid": int(cp.stdout.strip()), "launcher": "WIN32_PROCESS_CIM"}

def _spawn_direct(worker_path: str) -> dict:
    flags = 0
    if os.name == "nt":
        flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        flags |= getattr(subprocess, "DETACHED_PROCESS", 0)
        if _current_process_in_job():
            flags |= getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0x01000000)
    p = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "monitor", str(Path(worker_path).resolve())],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        shell=False,
        creationflags=flags,
        cwd=str(Path(__file__).resolve().parent),
    )
    return {"status": "STARTED", "pid": p.pid, "launcher": "DETACHED_BREAKAWAY" if os.name == "nt" else "DETACHED"}

def _record_launch(result: dict, *, reason: str, fallback_error: str | None = None) -> dict:
    payload = {
        "schema": "build2.supervisor_launch/1",
        "build2_version": BUILD2_VERSION,
        "timestamp_utc": utc(),
        "reason": reason,
        **result,
    }
    if fallback_error:
        payload["fallback_error"] = fallback_error[-1200:]
    atomic_json(SUPERVISOR_LAUNCH, payload)
    return result

def ensure_persistent_supervisor(worker_path: str) -> dict:
    cur = read_json(SUPERVISOR_PID, {}) or {}
    pid = int(cur.get("pid") or 0)
    if _pid_alive(pid):
        return _record_launch(
            {"status": "ALREADY_RUNNING", "pid": pid, "launcher": "EXISTING"},
            reason="existing durable supervisor"
        )

    if os.name == "nt":
        # A managed-app handler may itself be inside a short-lived Windows Job.
        # In that case prefer Win32_Process/CIM so the durable supervisor is
        # created by the OS management service rather than inheriting the
        # transient handler lifetime. This avoids the observed 0xC000013A class.
        if _current_process_in_job():
            try:
                return _record_launch(
                    _spawn_via_cim(worker_path),
                    reason="handler is inside a Windows Job; use OS-owned launch"
                )
            except Exception as cim_error:
                try:
                    return _record_launch(
                        _spawn_direct(worker_path),
                        reason="CIM unavailable; detached breakaway fallback",
                        fallback_error=repr(cim_error)
                    )
                except Exception:
                    raise cim_error

        try:
            return _record_launch(
                _spawn_direct(worker_path),
                reason="handler is not in a Windows Job; detached launch is sufficient"
            )
        except OSError as direct_error:
            return _record_launch(
                _spawn_via_cim(worker_path),
                reason="detached launch unavailable; OS-owned CIM fallback",
                fallback_error=repr(direct_error)
            )

    return _record_launch(_spawn_direct(worker_path), reason="non-Windows detached launch")

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "monitor":
        raise SystemExit(monitor(sys.argv[2]))
    raise SystemExit("USAGE: build2_supervisor.py monitor <build2_worker.py>")
