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
import socketserver
import threading
import re
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
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("X-Bridge-Signature", bridge.sig(f"{nonce}\n{status}\n{hashlib.sha256(content).hexdigest()}"))
                self.end_headers()
                self.wfile.write(content)
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                # Client dropped during a bounded response. Do not retry a second HTTP reply.
                return
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

DISCOVERY_PORT = 8767
_DISCOVERY_NONCE = re.compile(rb"^[0-9a-f]{32}$")


def discovery_handler_factory(agent_port):
    """Unauthenticated, USB-bound *address discovery only*; never shares keys.

    Caller must bind this UDP server to the same private USB interface as HTTP.
    No command or file operations are exposed by this handler.
    """
    class DiscoveryHandler(socketserver.BaseRequestHandler):
        def handle(self):
            packet, sock = self.request
            if len(packet) != 58 or not packet.startswith(b"BCP_USB_RESCUE_DISCOVER/1 "):
                return
            nonce = packet.split(b" ", 1)[1]
            if not _DISCOVERY_NONCE.fullmatch(nonce):
                return
            sender = self.client_address[0]
            try:
                sender_ip = ipaddress.ip_address(sender)
                if not (sender_ip.is_private or sender_ip.is_loopback):
                    return
            except ValueError:
                return
            reply = b"BCP_USB_RESCUE_HERE/1 " + nonce + b" " + str(agent_port).encode("ascii")
            sock.sendto(reply, self.client_address)
    return DiscoveryHandler


def start_discovery_listener(host, agent_port, discovery_port=DISCOVERY_PORT):
    """Returns a UDPServer for tests or production; caller must close it."""
    server = socketserver.UDPServer((host, discovery_port), discovery_handler_factory(agent_port))
    server.allow_reuse_address = False
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
    thread.start()
    return server


REVERSE_PORT = 8768
REVERSE_ENDPOINTS = {"/v1/status": "status", "/v1/diagnostics": "diagnostics",
                     "/v1/files": "files", "/v1/read": "read", "/v1/write": "write",
                     "/v1/audit": "audit"}


def reverse_once(bridge, pc_usb_ip, phone_ip, port=REVERSE_PORT, timeout=5):
    """PC dials phone over tether. No inbound Windows firewall opening is needed.

    A HELLO is not proof of pairing. All actual commands require HMAC exactly as HTTP.
    This method handles exactly one bounded RPC per connection and closes the socket.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.bind((pc_usb_ip, 0))
        s.connect((phone_ip, port))
        s.sendall(b"BCP_USB_RESCUE_PC_HELLO/1\n")
        frame = s.makefile("rb").readline(MAX_BODY * 4 + 2048)
        if not frame or len(frame) > MAX_BODY * 4 or not frame.endswith(b"\n"):
            return "PRESENCE_ONLY"
        packet = json.loads(frame.decode("utf-8"))
        if not isinstance(packet, dict) or packet.get("endpoint") not in REVERSE_ENDPOINTS:
            return "INVALID_ENDPOINT"
        path = packet["endpoint"]
        body_text = packet.get("body")
        if not isinstance(body_text, str):
            return "INVALID_BODY"
        body = body_text.encode("utf-8")
        if len(body) > MAX_BODY:
            return "BODY_TOO_LARGE"
        nonce, ts, signature = packet.get("nonce"), packet.get("timestamp"), packet.get("signature")
        error = bridge.authenticate("POST", path, ts, nonce, signature, body)
        if error:
            bridge.record(REVERSE_ENDPOINTS[path], error, str(nonce)[:90])
            code, payload = 401, {"ok": False, "reason": error}
        else:
            try:
                result = bridge.operate(REVERSE_ENDPOINTS[path], json.loads(body.decode("utf-8")))
                bridge.record(REVERSE_ENDPOINTS[path], "SUCCESS", nonce)
                code, payload = 200, {"ok": True, "result": result}
            except (ValueError, UnicodeError, TypeError, OSError) as exc:
                reason = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
                bridge.record(REVERSE_ENDPOINTS[path], reason, nonce)
                code, payload = 400, {"ok": False, "reason": reason}
        content = compact(payload)
        mac = bridge.sig(f"{nonce}\n{code}\n{hashlib.sha256(content).hexdigest()}")
        reply = compact({"status": code, "body": content.decode("utf-8"), "signature": mac}) + b"\n"
        if len(reply) > MAX_BODY * 4:
            return "RESPONSE_TOO_LARGE"
        s.sendall(reply)
        return "RPC_REPLIED"


def reverse_worker(bridge, pc_usb_ip, phone_ip):
    """Bounded opportunistic outbound reconnect. Never connects outside USB /24."""
    src = ipaddress.ip_address(pc_usb_ip)
    dst = ipaddress.ip_address(phone_ip)
    if src.version != 4 or dst.version != 4 or dst not in ipaddress.ip_network(f"{src}/24", strict=False):
        raise ValueError("PHONE_GATEWAY_MUST_SHARE_USB_SUBNET")
    while True:
        try:
            reverse_once(bridge, pc_usb_ip, phone_ip, timeout=4)
        except (OSError, ValueError, TimeoutError):
            pass
        time.sleep(2)


def serve(bridge, host, port, reverse_peer=None):
    httpd=ThreadingHTTPServer((host, port),handler_factory(bridge))
    if reverse_peer is not None:
        threading.Thread(target=reverse_worker, args=(bridge, host, reverse_peer), daemon=True).start()
    httpd.daemon_threads = True
    discovery = None
    try:
        discovery = start_discovery_listener(host, httpd.server_port)
        print("USB discovery listening on UDP", DISCOVERY_PORT)
    except OSError as exc:
        print("USB_DISCOVERY_UNAVAILABLE:", type(exc).__name__, str(exc))
    print(f"BCP USB Rescue Windows agent on http://{host}:{httpd.server_port}")
    print("IMPORTANT: unencrypted USB/private LAN prototype; NEVER forward this port to public Internet.")
    print("Pairing key stored in state directory. Never transmit it via public chat or logs.")
    print("Workspace:",bridge.workspace)
    try: httpd.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt: pass
    finally:
        httpd.server_close()
        if discovery is not None:
            discovery.shutdown()
            discovery.server_close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bind",default="127.0.0.1",help="USB tether adapter IPv4; default loopback for safety")
    p.add_argument("--port",type=int,default=8876)
    p.add_argument("--reverse-peer",default=None,help="USB tether gateway phone IPv4; outbound only")
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
    if args.reverse_peer:
        try:
            peer = ipaddress.ip_address(args.reverse_peer)
            if peer.version != 4 or peer not in ipaddress.ip_network(f"{addr}/24", strict=False):
                p.error("reverse peer must be on the same USB /24")
        except ValueError:
            p.error("reverse peer must be a private USB IPv4")
    serve(Bridge(args.state,args.workspace),args.bind,args.port,args.reverse_peer)
if __name__=="__main__": main()