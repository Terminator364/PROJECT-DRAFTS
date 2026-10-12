#!/usr/bin/env python3
"""BCP USB Rescue PC R3.1 — standalone Windows installer/control panel.

Packaged by PyInstaller with a separately frozen, bounded bridge_agent.exe.
This launcher never downloads programs, exposes secrets to logs, or silently
changes Windows network/firewall policy. Pairing secret remains on this PC.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox

APP_NAME = "BCP USB Rescue PC"
APP_VERSION = "3.1-pilot"
INSTALL_NAME = "BCP-USB-Rescue"
PORT = 8766
REQUIRED = (
    "bridge_agent.exe", "bridge_agent.py", "Start-Bridge.ps1",
    "Install-Rescue.ps1", "Usb-Readiness.ps1", "Fix-UsbFirewall.ps1",
    "Request-UsbFirewall.ps1", "REMOVE.cmd",
)


def payload_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "windows"


def install_root() -> Path:
    base = os.environ.get("LOCALAPPDATA", "").strip()
    if not base:
        raise RuntimeError("Windows LOCALAPPDATA introuvable")
    return Path(base) / INSTALL_NAME


def validate_payload() -> tuple[bool, str]:
    missing = [p for p in REQUIRED if not (payload_root() / p).is_file()]
    if missing:
        return False, "Fichiers manquants : " + ", ".join(missing)
    return True, "Fichiers Windows intégrés : OK"


def run_powershell(script: Path, *, timeout=90, extras: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    if not script.is_file():
        raise FileNotFoundError(str(script))
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script), *extras],
        capture_output=True, text=True, errors="replace", timeout=timeout, creationflags=flags,
    )


def get_pairing_key(*, create=False) -> str | None:
    path = install_root() / "private-state" / "pairing-key.txt"
    if path.exists():
        key = path.read_text(encoding="utf-8-sig").strip()
        if len(key) != 64 or any(c not in "0123456789abcdefABCDEF" for c in key):
            raise RuntimeError("Clé d'appairage existante invalide : sécurité bloquée.")
        return key
    if not create:
        return None
    # The Installer PS has already created and hardened private-state ACLs.
    if not path.parent.is_dir():
        raise RuntimeError("Le dossier sécurisé n'existe pas. Relance l'installation.")
    key = secrets.token_hex(32)
    try:
        with path.open("x", encoding="ascii") as out:
            out.write(key + "\n")
    except FileExistsError:
        return get_pairing_key(create=False)
    return key


def usb_summary() -> dict:
    script = install_root() / "windows" / "Usb-Readiness.ps1"
    if not script.is_file():
        return {"installed": False, "reason": "L'agent PC n'est pas encore installé."}
    result = run_powershell(script, timeout=20)
    if result.returncode != 0:
        return {"installed": True, "reason": "Diagnostic Windows inaccessible : " + (result.stderr or "Erreur PowerShell")[:300]}
    data = json.loads(result.stdout)
    return {"installed": True, **data}


def pick_ip(snapshot: dict) -> str | None:
    adapters = snapshot.get("usb_adapters") or []
    if isinstance(adapters, dict):
        adapters = [adapters]
    valid = [str(item.get("ip", "")) for item in adapters if isinstance(item, dict) and item.get("ip")]
    return valid[0] if len(valid) == 1 else None


def begin_guardian() -> None:
    script = install_root() / "windows" / "Start-Bridge.ps1"
    if not script.is_file():
        raise RuntimeError("Le superviseur Windows n'est pas installé.")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    subprocess.Popen([
        "powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden",
        "-ExecutionPolicy", "Bypass", "-File", str(script)
    ], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
       creationflags=flags, close_fds=True)


def install() -> str:
    ok, detail = validate_payload()
    if not ok:
        raise RuntimeError(detail)
    result = run_powershell(payload_root() / "Install-Rescue.ps1", timeout=90)
    if result.returncode:
        raise RuntimeError("Installation Windows échouée :\n" + (result.stderr or result.stdout)[-1600:])
    get_pairing_key(create=True)
    begin_guardian()
    return "Agent installé, clé locale préparée et superviseur démarré.\n" + result.stdout[-850:]


def cli_self_test() -> int:
    ok, msg = validate_payload()
    data = {"name": APP_NAME, "version": APP_VERSION, "bundle_ok": ok,
            "protocol_port": PORT, "uses_windows_python": False,
            "real_pc_usb_validation": "NOT_RUN", "result": msg}
    if sys.stdout is not None:
        print(json.dumps(data, ensure_ascii=False))
    return 0 if ok else 1


class RescueUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("BCP USB Rescue — Mon ordinateur")
        self.window.geometry("635x680")
        self.window.minsize(505, 580)
        self.window.configure(bg="#f4f6f9")
        self.busy = False
        self.current_ip = None
        self.last_snapshot = {}
        self.status_var = tk.StringVar(value="Vérification de la liaison...")
        self.detail_var = tk.StringVar(value="Branche ton Samsung et active le partage USB.")
        self.ip_var = tk.StringVar(value="Non détectée")
        self.install_var = tk.StringVar(value="Installation non vérifiée")
        self._build()
        self.refresh()
        self.window.after(25000, self._periodic)

    def label(self, parent, txt, size=11, color="#1b2e48", bold=False, pady=0):
        return tk.Label(parent, text=txt, font=("Segoe UI", size, "bold" if bold else "normal"),
                        bg=parent.cget("bg"), fg=color, justify="left", anchor="w",
                        wraplength=540, pady=pady)

    def button(self, parent, title, handler, primary=False):
        b = tk.Button(parent, text=title, command=handler, font=("Segoe UI", 11, "bold"),
                      bg="#0b737c" if primary else "#e3f1f1", fg="white" if primary else "#0a606a",
                      activebackground="#095c64", activeforeground="white" if primary else "#172c3f",
                      padx=15, pady=11, relief="flat", cursor="hand2")
        return b

    def _build(self):
        shell = tk.Frame(self.window, bg="#f4f6f9", padx=22, pady=16)
        shell.pack(fill="both", expand=True)
        self.label(shell, "BCP / USB RESCUE", 11, "#0b737c", True).pack(fill="x")
        self.label(shell, "Mon ordinateur · MBMPC", 23, "#132b40", True, 4).pack(fill="x")
        self.label(shell, "Liaison sécurisée locale entre le Samsung et Windows", 11, "#586a7b").pack(fill="x", pady=(0,15))
        card = tk.Frame(shell, bg="white", padx=17, pady=14, highlightbackground="#e4e9ec", highlightthickness=1)
        card.pack(fill="x", pady=(0,14))
        self.label(card,"ÉTAT DU LIEN",10,"#0b737c",True).pack(fill="x")
        tk.Label(card,textvariable=self.status_var,font=("Segoe UI",18,"bold"),bg="white",fg="#172b43",anchor="w",wraplength=520).pack(fill="x",pady=(6,3))
        tk.Label(card,textvariable=self.detail_var,font=("Segoe UI",10),bg="white",fg="#607187",anchor="w",justify="left",wraplength=520).pack(fill="x",pady=(0,12))
        self.button(card,"Installer et activer sur ce PC",self.install_clicked,True).pack(fill="x",pady=3)
        self.button(card,"Actualiser le diagnostic",self.refresh).pack(fill="x",pady=3)
        self.label(card,"Adresse USB du PC",10,"#64748b").pack(fill="x",pady=(10,0))
        tk.Label(card,textvariable=self.ip_var,font=("Segoe UI",16,"bold"),bg="white",fg="#0b737c").pack(anchor="w")
        self.button(card,"Copier l’adresse IP",self.copy_ip).pack(fill="x",pady=(5,3))
        self.button(card,"Copier la clé d’appairage",self.copy_key).pack(fill="x",pady=3)
        self.label(card,"Ne partage jamais la clé dans un message ou une capture.",9,"#9e4b36").pack(fill="x")
        sec = tk.Frame(shell, bg="white", padx=17, pady=12, highlightbackground="#e4e9ec", highlightthickness=1)
        sec.pack(fill="x")
        self.label(sec,"SI LE TÉLÉPHONE NE SE CONNECTE PAS",10,"#0b737c",True).pack(fill="x")
        self.button(sec,"Vérifier / réparer le pare-feu USB (avec accord Windows)",self.firewall_clicked).pack(fill="x",pady=7)
        self.label(sec,"Le port 8766 n'est jamais ouvert automatiquement à tous les réseaux.",9,"#667788").pack(fill="x")
        tk.Label(shell,textvariable=self.install_var,font=("Segoe UI",9),bg="#f4f6f9",fg="#63758b",anchor="w",justify="left",wraplength=530).pack(fill="x",pady=(8,0))
        self.label(shell,"Prototype local : pas de contrôle à distance complet de Windows, ni de connexion ChatGPT automatique.",9,"#7c6262").pack(fill="x",pady=(5,0))

    def _thread(self, function, on_success):
        if self.busy:return
        self.busy=True
        self.status_var.set("Opération Windows en cours...")
        def worker():
            try:
                result=function()
                self.window.after(0,lambda:finish(result,None))
            except Exception as e:
                err=str(e)
                self.window.after(0,lambda:finish(None,err))
        def finish(value,error):
            self.busy=False
            if error:
                self.status_var.set("Action interrompue")
                self.detail_var.set(error)
                messagebox.showerror(APP_NAME,error,parent=self.window)
            else:
                on_success(value)
        threading.Thread(target=worker,daemon=True).start()

    def install_clicked(self):
        if not messagebox.askyesno(APP_NAME,"Installer l'agent local BCP USB Rescue pour ton utilisateur Windows et configurer son redémarrage automatique ?\n\nAucun pare-feu ne sera ouvert sans autorisation séparée.",parent=self.window):
            return
        self._thread(install, lambda detail: (self.install_var.set("Agent installé"),self.detail_var.set(detail.splitlines()[0]),self.refresh()))

    def refresh(self):
        if self.busy:return
        def update(snapshot):
            self.last_snapshot=snapshot
            self.current_ip=pick_ip(snapshot)
            self.ip_var.set(self.current_ip or "Non détectée : activer partage USB")
            if not snapshot.get("installed"):
                self.status_var.set("Agent Windows à installer")
                self.detail_var.set("Appuie sur Installer et activer sur ce PC.")
                self.install_var.set("Installation requise")
            elif not self.current_ip:
                self.status_var.set("En attente du câble USB")
                self.detail_var.set("Branche le téléphone et active Paramètres → Partage de connexion → Partage USB.")
                self.install_var.set("Agent installé — câble USB en attente")
            elif snapshot.get("agent_listener_found"):
                self.status_var.set("PC détecté sur USB")
                self.detail_var.set("Copie l’adresse IP et la clé dans Réglages de l’APK Samsung. Port 8766.")
                self.install_var.set("Agent prêt localement — validation téléphone nécessaire")
            else:
                self.status_var.set("USB détecté ; agent en démarrage")
                self.detail_var.set("Vérifie le superviseur Windows ou redémarre l'installation.")
                self.install_var.set("Liaison réseau présente")
        self._thread(usb_summary,update)

    def _periodic(self):
        if not self.busy:self.refresh()
        self.window.after(25000,self._periodic)

    def _copy(self,value,description):
        if not value:
            messagebox.showinfo(APP_NAME,"Information non disponible pour le moment.",parent=self.window);return
        self.window.clipboard_clear()
        self.window.clipboard_append(value)
        self.window.update()
        messagebox.showinfo(APP_NAME,description+" copiée. Colle-la uniquement dans Réglages de BCP USB Rescue sur ton téléphone.",parent=self.window)

    def copy_ip(self):
        self._copy(self.current_ip,"Adresse IP USB")

    def copy_key(self):
        try: self._copy(get_pairing_key(create=False),"Clé d’appairage")
        except Exception as e: messagebox.showerror(APP_NAME,str(e),parent=self.window)

    def firewall_clicked(self):
        if not messagebox.askyesno(APP_NAME,"En cas de connexion bloquée uniquement : autoriser la règle Windows entrante sur l'interface USB active et le port 8766 ? Windows demandera une confirmation administrateur. Aucune règle générale Wi-Fi ne sera ajoutée.",parent=self.window):return
        def go():
            script=install_root()/"windows"/"Request-UsbFirewall.ps1"
            res=run_powershell(script,timeout=100)
            if res.returncode:return "La correction a été refusée ou a échoué."
            return "Opération terminée ; recommence le diagnostic pour vérifier la règle."
        self._thread(go,lambda msg:(self.detail_var.set(msg),self.refresh()))

    def run(self):
        self.window.mainloop()


def main() -> int:
    if len(sys.argv)>1 and sys.argv[1]=="--self-test":
        return cli_self_test()
    if os.name!="nt":
        print("Ce programme est destiné à Windows 10/11.",file=sys.stderr)
        return 2
    RescueUI().run()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())