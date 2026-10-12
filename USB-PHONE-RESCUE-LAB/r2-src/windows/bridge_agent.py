#!/usr/bin/env python3
"""BCP USB Rescue R1: authenticated local transport and bounded file operations.

Not exposed to the Internet by default. This is a supervised, LOCAL-USB prototype.
Only one workspace may be accessed. No arbitrary shell/remote-desktop API.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import platform
import secrets
import socket
import ipaddress
import sqlite3
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import RLock
from contextlib import contextmanager

MAX_BODY = 128 * 1024
MAX_FILE = 64 * 1024
MAX_SKEW = 120

def compact(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

class Bridge:
    def __init__(self, state_dir: Path, workspace: Path, secret: str | None = None):
        self.state_dir = Path(state_dir).resolve()
        self.workspace = Path(workspace).resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.secret_path = self.state_dir / "pairing-key.txt"
        if secret is None:
            if not self.secret_path.exists():
                k = secrets.token_hex(32)
                # Windows ACL comes from current user directory; do not use shared location.
                with self.secret_path.open("x", encoding="utf-8") as f: f.write(k + "\n")
                if os.name != "nt": self.secret_path.chmod(0o600)
            secret = self.secret_path.read_text(encoding="utf-8").strip()
        if len(secret) < 32:
            raise ValueError("pairing key too short")
        self.key = secret.encode("utf-8")
        self.db_path = self.state_dir / "audit.sqlite3"
        self.lock = RLock()
        with self.db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS seen (nonce TEXT PRIMARY KEY, seen_at INTEGER NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY, at INTEGER, action TEXT, result TEXT, nonce TEXT)")
    @contextmanager
    def db(self):
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        try:
            with conn:
                yield conn
        finally:
            conn.close()
    def sig(self, msg: str):
        return hmac.new(self.key, msg.encode("utf-8"), hashlib.sha256).hexdigest()
    def authenticate(self, method, path, ts, nonce, signature, body):
        try: t = int(ts)
        except (TypeError, ValueError): return "BAD_TIMESTAMP"
        if abs(time.time() - t) > MAX_SKEW: return "STALE_TIMESTAMP"
        if not isinstance(nonce, str) or not (16 <= len(nonce) <= 90) or not all(c.isalnum() or c in "-_" for c in nonce):
            return "BAD_NONCE"
        digest = hashlib.sha256(body).hexdigest()
        expected = self.sig(f"{method}\n{path}\n{ts}\n{nonce}\n{digest}")
        if not hmac.compare_digest(expected, signature or ""): return "BAD_SIGNATURE"
        with self.lock:
            with self.db() as db:
                db.execute("DELETE FROM seen WHERE seen_at < ?", (int(time.time())-MAX_SKEW*2,))
                try: db.execute("INSERT INTO seen VALUES (?, ?)", (nonce, int(time.time())))
                except sqlite3.IntegrityError: return "REPLAY"
        return None
    def record(self, action, result, nonce):
        with self.lock:
            with self.db() as db:
                db.execute("INSERT INTO actions(at,action,result,nonce) VALUES (?,?,?,?)", (int(time.time()), action, result, nonce))
    def safe_path(self, name):
        if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
            raise ValueError("INVALID_PATH")
        resolved = (self.workspace / name).resolve(strict=False)
        if not resolved.is_relative_to(self.workspace) or resolved == self.workspace:
            raise ValueError("OUTSIDE_WORKSPACE")
        return resolved
    def operate(self, action, payload):
        if not isinstance(payload, dict): raise ValueError("PAYLOAD_MUST_BE_OBJECT")
        if action == "status":
            return {"agent":"BCP_USB_RESCUE_R1","platform":platform.system(),"host":socket.gethostname(),
                    "workspace":str(self.workspace), "time_utc":datetime.now(timezone.utc).isoformat(),
                    "mode":"USB_OR_PRIVATE_LAN_LOCAL_ONLY", "tls":False,"arbitrary_shell":False}
        if action == "diagnostics":
            # Fixed, read-only probes; no remote input interpolated into commands.
            import shutil
            return {"python":platform.python_version(),"os":platform.platform(),
                    "hostname":socket.gethostname(),"workspace_exists":self.workspace.is_dir(),
                    "free_disk_bytes":shutil.disk_usage(self.workspace).free,
                    "desktop_commander_remote":"NOT_TESTED_BY_THIS_AGENT",
                    "usb_adapter":"FIELD_TEST_REQUIRED"}
        if action == "files":
            return {"items":[{"name":p.name,"kind":"dir" if p.is_dir() else "file"} for p in sorted(self.workspace.iterdir())[:100]]}
        if action == "read":
            p = self.safe_path(payload.get("path"))
            if not p.is_file(): raise ValueError("NO_SUCH_FILE")
            if p.stat().st_size > MAX_FILE: raise ValueError("FILE_TOO_LARGE")
            return {"path":str(p.relative_to(self.workspace)),"content":p.read_text(encoding="utf-8"),
                    "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
        if action == "write":
            if payload.get("approved") is not True: raise ValueError("APPROVAL_REQUIRED")
            p = self.safe_path(payload.get("path"))
            content = payload.get("content")
            if not isinstance(content, str) or len(content.encode("utf-8")) > MAX_FILE: raise ValueError("CONTENT_INVALID_OR_TOO_LARGE")
            if not p.parent.is_dir(): raise ValueError("PARENT_MISSING")
            previous = p.read_bytes() if p.exists() and p.is_file() else None
            if previous is not None and len(previous)>MAX_FILE: raise ValueError("EXISTING_FILE_TOO_LARGE")
            if previous is not None:
                backup = self.state_dir / ("backup_" + secrets.token_hex(10) + ".bin")
                backup.write_bytes(previous)
            else: backup = None
            temp = p.with_name("."+p.name+"."+secrets.token_hex(5)+".tmp")
            try:
                temp.write_text(content, encoding="utf-8")
                os.replace(temp, p)
            finally:
                if temp.exists(): temp.unlink()
            return {"path":str(p.relative_to(self.workspace)),"bytes":len(content.encode('utf-8')),
                    "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                    "backup_name":backup.name if backup else None}
        if action == "audit":
            with self.db() as db:
                rows = db.execute("SELECT at,action,result FROM actions ORDER BY id DESC LIMIT 20").fetchall()
            return {"events":[{"at":a,"action":b,"result":c} for a,b,c in rows]}
        raise ValueError("ACTION_NOT_ALLOWED")

def handler_factory(bridge):
    class Handler(BaseHTTPRequestHandler):
        server_version = "BCP-USB-Rescue/0.1"
        def log_message(self,*args): pass
        def response(self, status, payload, nonce=""):
            content = compact(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("X-Bridge-Signature", bridge.sig(f"{nonce}\n{status}\n{hashlib.sha256(content).hexdigest()}"))
            self.end_headers()
            self.wfile.write(content)
        def do_GET(self):
            if self.path != "/health": return self.response(404,{"ok":False,"reason":"NOT_FOUND"})
            return self.response(200,{"ok":True,"service":"BCP-USB-RESCUE","protocol":1})
        def do_POST(self):
            allowed = {"/v1/status":"status","/v1/diagnostics":"diagnostics", "/v1/files":"files",
                       "/v1/read":"read","/v1/write":"write","/v1/audit":"audit"}
            if self.path not in allowed: return self.response(404,{"ok":False,"reason":"NOT_FOUND"}, self.headers.get("X-Bridge-Nonce", ""))
            try: n = int(self.headers.get("Content-Length", "-1"))
            except ValueError: n = -1
            if n < 0 or n > MAX_BODY: return self.response(413,{"ok":False,"reason":"BODY_SIZE_INVALID"})
            body = self.rfile.read(n)
            nonce = self.headers.get("X-Bridge-Nonce", "")
            error = bridge.authenticate("POST",self.path,self.headers.get("X-Bridge-Time"),nonce,
                                        self.headers.get("X-Bridge-Signature", ""),body)
            if error:
                bridge.record(allowed[self.path],error,nonce[:90])
                return self.response(401,{"ok":False,"reason":error},nonce)
            try:
                payload = json.loads(body.decode("utf-8"))
                value = bridge.operate(allowed[self.path],payload)
                bridge.record(allowed[self.path],"SUCCESS",nonce)
                return self.response(200,{"ok":True,"result":value},nonce)
            except (ValueError,UnicodeError,TypeError,OSError) as exc:
                reason = str(exc) if isinstance(exc,ValueError) else type(exc).__name__
                bridge.record(allowed[self.path],reason,nonce)
                return self.response(400,{"ok":False,"reason":reason},nonce)
    return Handler

def serve(bridge, host, port):
    httpd=ThreadingHTTPServer((host, port),handler_factory(bridge))
    httpd.daemon_threads = True
    print(f"BCP USB Rescue Windows agent on http://{host}:{httpd.server_port}")
    print("IMPORTANT: unencrypted USB/private LAN prototype; NEVER forward this port to public Internet.")
    print("Pairing key stored in state directory. Never transmit it via public chat or logs.")
    print("Workspace:",bridge.workspace)
    try: httpd.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt: pass
    finally: httpd.server_close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bind",default="127.0.0.1",help="USB tether adapter IPv4; default loopback for safety")
    p.add_argument("--port",type=int,default=8766)
    p.add_argument("--state",type=Path,default=Path.home()/".bcp-usb-rescue")
    p.add_argument("--workspace",type=Path,default=Path.home()/"BCP-Rescue-Workspace")
    args=p.parse_args()
    try:
        addr = ipaddress.ip_address(args.bind)
    except ValueError:
        p.error("bind must be an IPv4 address of the local USB network adapter")
    if addr.version != 4 or not (addr.is_loopback or addr in ipaddress.ip_network('10.0.0.0/8') or
       addr in ipaddress.ip_network('172.16.0.0/12') or addr in ipaddress.ip_network('192.168.0.0/16')):
        p.error("Refusing public/non-local listener: choose USB adapter private IPv4 or loopback")
    if not 1024 <= args.port <= 65535: p.error("port must be 1024..65535")
    serve(Bridge(args.state,args.workspace),args.bind,args.port)
if __name__=="__main__": main()