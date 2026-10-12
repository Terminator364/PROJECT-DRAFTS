"""Generate short-lived read-only Android mission JSON for user-mediated handoff.

Example: python tools_mission_generator.py diagnostics --out diagnostic.json
No connection to ChatGPT or Windows is initiated by this script.
"""
import argparse
import json
import time
from pathlib import Path

SAFE_ACTIONS = {'status','diagnostics','files','read','audit'}

def build(action, *, path='', minutes=60, now=None):
    if action not in SAFE_ACTIONS:
        raise ValueError('Only read-only actions are generated; Windows writes require manual user approval')
    if not 1 <= minutes <= 1440:
        raise ValueError('Expiry must be between 1 and 1440 minutes')
    payload={}
    if action == 'read':
        if not path or len(path)>240 or path.startswith('/') or '\\' in path or '..' in path.split('/'):
            raise ValueError('Relative sandbox filename required')
        payload['path']=path
    elif path:
        raise ValueError('Path argument only allowed for read')
    return {'schema':'bcp-rescue-mission/1','action':action,
            'expires_unix_seconds':int(time.time() if now is None else now)+minutes*60,
            'payload':payload}

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=sorted(SAFE_ACTIONS))
    ap.add_argument('--path',default='')
    ap.add_argument('--minutes',type=int,default=60)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    body=build(args.action,path=args.path,minutes=args.minutes)
    args.out.write_text(json.dumps(body,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Mission file:',args.out,'expires at Unix',body['expires_unix_seconds'])