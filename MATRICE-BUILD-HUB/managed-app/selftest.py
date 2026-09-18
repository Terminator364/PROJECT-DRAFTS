from __future__ import annotations
import ast
from pathlib import Path

root=Path(__file__).resolve().parent
bridge=root/"bridge.py"
if not bridge.is_file():
    raise SystemExit("MISSING:bridge.py")
text=bridge.read_text(encoding="utf-8")
ast.parse(text,filename=str(bridge))
required=[
    'REPO="Terminator364/PROJECT-DRAFTS"',
    'SOURCE_SHA="7d61ab980d6718fdb49322282bf00c56fe9bb7c8"',
    '"doctor":["-Mode","Doctor"]',
    '"build_phonemouse":["-Project","PhoneMouse","-Mode","Build"]',
    '"build_p2pcr95":["-Project","P2PCR95","-Mode","Build"]',
    '"build_chatgpt_pc":["-Project","ChatGPT-PC","-Mode","Build"]',
    'shell=False',
    '"reset","--hard",SOURCE_SHA',
    '"rev-parse","HEAD"',
    'SOURCE_SHA_MISMATCH',
]
for token in required:
    if token not in text:
        raise SystemExit("TOKEN_MISSING:"+token)
for forbidden in ["shell=True","cmd.exe /c","powershell -Command","os.system(","subprocess.call("]:
    if forbidden in text:
        raise SystemExit("FORBIDDEN:"+forbidden)
print("MBH_MANAGED_APP_SELFTEST_PASS")
