import asyncio, base64, getpass, hashlib, hmac, json, os, sys, tempfile, time
from pathlib import Path
import requests
import win32crypt
from telethon import TelegramClient, events

APP = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "ChatGPTDeliveryXL"
APP.mkdir(parents=True, exist_ok=True)
CFG = APP / "config.dpapi"
STATE = APP / "state.json"
SESSION = APP / "telegram-bot"
PART = 6_000_000

def protect(data: bytes) -> bytes:
    return win32crypt.CryptProtectData(data, "ChatGPTDeliveryXL", None, None, None, 0)[1]

def unprotect(data: bytes) -> bytes:
    return win32crypt.CryptUnprotectData(data, None, None, None, 0)[1]

def save_config(cfg):
    CFG.write_bytes(protect(json.dumps(cfg).encode("utf-8")))

def load_config():
    if not CFG.exists():
        return None
    return json.loads(unprotect(CFG.read_bytes()).decode("utf-8"))

def setup():
    print("\nChatGPT Delivery XL — configuration unique\n")
    api_id = int(input("Telegram API ID (my.telegram.org): ").strip())
    api_hash = getpass.getpass("Telegram API Hash: ").strip()
    bot_token = getpass.getpass("Bot Token: ").strip()
    url = input("URL Web App Apps Script V9.0.1: ").strip()
    owner = input("Telegram ID propriétaire [1298744015]: ").strip() or "1298744015"
    cfg = {"api_id":api_id,"api_hash":api_hash,"bot_token":bot_token,"url":url,"owner":int(owner)}
    save_config(cfg)
    try:
        startup = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup/ChatGPT-Delivery-XL.cmd"
        exe = Path(sys.executable).resolve()
        startup.write_text(f'@echo off\nstart "" /min "{exe}"\n', encoding="utf-8")
        print("Démarrage automatique Windows activé.")
    except Exception as e:
        print("Démarrage auto non créé:", e)
    return cfg

def load_state():
    try: return json.loads(STATE.read_text(encoding="utf-8"))
    except: return {"done":[]}

def save_state(s):
    STATE.write_text(json.dumps(s), encoding="utf-8")

def sig(token, transfer_id, filename, idx, total, sha, b64len):
    canonical = "|".join(map(str,[transfer_id,filename,idx,total,sha,b64len]))
    return hmac.new(token.encode(), canonical.encode(), hashlib.sha256).hexdigest()

def post_part(cfg, payload):
    for attempt in range(1,5):
        try:
            r=requests.post(cfg["url"], json=payload, timeout=120)
            d=r.json()
            if r.ok and d.get("ok"): return d
            err=d.get("error", r.text[:200])
            if "BAD_SIGNATURE" in str(err): raise RuntimeError(err)
        except Exception as e:
            if attempt==4: raise
        time.sleep(min(15, attempt*2))
    raise RuntimeError("upload failed")

async def process_message(client, cfg, message, state):
    if not message.media or not message.file:
        return
    size = int(message.file.size or 0)
    if size <= 18_000_000:
        return
    key = str(message.id)
    if key in state["done"]:
        return

    name = message.file.name or f"telegram-{message.id}.bin"
    transfer_id = f"XL-{message.id}-{message.sender_id}"
    tmpdir = Path(tempfile.mkdtemp(prefix="cdxl-"))
    path = tmpdir / name
    try:
        await client.send_message(cfg["owner"], f"🧩 XL démarre • {name} • {size/1_000_000:.1f} MB")
        await message.download_media(file=str(path))
        total = (path.stat().st_size + PART - 1) // PART
        with path.open("rb") as fh:
            for idx in range(total):
                chunk=fh.read(PART)
                sha=hashlib.sha256(chunk).hexdigest()
                b64=base64.b64encode(chunk).decode("ascii")
                payload={
                    "transfer_id":transfer_id,
                    "filename":name,
                    "part_index":idx,
                    "parts_total":total,
                    "sha256":sha,
                    "data_b64":b64,
                }
                payload["signature"]=sig(cfg["bot_token"],transfer_id,name,idx,total,sha,len(b64))
                await asyncio.to_thread(post_part,cfg,payload)
                await client.send_message(cfg["owner"], f"🧩 XL {idx+1}/{total} • {name}")
        state["done"].append(key)
        state["done"]=state["done"][-500:]
        save_state(state)
        await client.send_message(cfg["owner"], f"✅ XL prêt pour ChatGPT • {name}")
    except Exception as e:
        await client.send_message(cfg["owner"], f"⚠️ XL en pause • {name}\n{type(e).__name__}: {str(e)[:160]}")
    finally:
        try:
            if path.exists(): path.unlink()
            tmpdir.rmdir()
        except: pass

async def main():
    cfg=load_config() or setup()
    state=load_state()
    client=TelegramClient(str(SESSION), cfg["api_id"], cfg["api_hash"],
                          sequential_updates=True, catch_up=True,
                          connection_retries=10, request_retries=5, retry_delay=2)
    await client.start(bot_token=cfg["bot_token"])
    me=await client.get_me()
    print(f"ChatGPT Delivery XL actif: @{me.username or me.id}")

    @client.on(events.NewMessage(from_users=cfg["owner"]))
    async def inbound(event):
        await process_message(client,cfg,event.message,state)

    await client.send_message(cfg["owner"], "🟢 Bridge XL connecté.")
    await client.run_until_disconnected()

if __name__=="__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
    except Exception as e:
        print("ERREUR:",repr(e))
        input("Entrée pour fermer...")
