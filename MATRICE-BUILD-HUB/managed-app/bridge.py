from __future__ import annotations

import json
import sys

from build2_core import LATEST, get_receipt, read_json, request_cancel
from build2_worker import enqueue, latest_status

OPERATIONS={
    "doctor":("BuildHub","doctor"),
    "build_phonemouse":("PhoneMouse","build_phonemouse"),
    "build_p2pcr95":("P2PCR95","build_p2pcr95"),
    "build_chatgpt_pc":("ChatGPT-PC","build_chatgpt_pc"),
}

def emit(data:dict)->int:
    print(json.dumps(data,ensure_ascii=False))
    return 0

def latest_identity()->tuple[str|None,str|None]:
    x=read_json(LATEST,{}) or {}
    return x.get("project"),x.get("run_id")

def run(operation:str)->int:
    if operation in OPERATIONS:
        project,op=OPERATIONS[operation]
        return emit({"schema":"mbh-managed-bridge-result-v5","operation":operation,**enqueue(project,op)})
    if operation=="last_build_status":
        return emit({"schema":"mbh-managed-bridge-result-v5","operation":operation,**latest_status()})
    if operation=="get_receipt":
        project,run_id=latest_identity()
        if not project or not run_id:
            return emit({"schema":"mbh-managed-bridge-result-v5","status":"NO_RUN"})
        return emit({"schema":"mbh-managed-bridge-result-v5","operation":operation,
                     "project":project,"run_id":run_id,"receipt":get_receipt(project,run_id)})
    if operation=="cancel_build":
        project,run_id=latest_identity()
        if not project or not run_id:
            return emit({"schema":"mbh-managed-bridge-result-v5","status":"NO_RUN"})
        return emit({"schema":"mbh-managed-bridge-result-v5","operation":operation,
                     "project":project,**request_cancel(project,run_id)})
    return emit({"schema":"mbh-managed-bridge-result-v5","status":"FAIL",
                 "code":"OPERATION_NOT_REGISTERED","operation":operation})

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("USAGE: bridge.py <named-operation>")
    raise SystemExit(run(sys.argv[1]))
