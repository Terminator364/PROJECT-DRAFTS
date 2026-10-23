#!/usr/bin/env python3
"""Append-only machine audit of new GitHub commits touching RIZ112.
A repository push is observable by CI; private ChatGPT chat messages are NOT.
This is a changelog of GitHub changes, not a full chat transcript.
"""
from __future__ import annotations
import json,os,subprocess,datetime,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
LOG=ROOT/'continuity'/'AUTO_GIT_EVENTS.jsonl'
CAHIER=ROOT/'CAHIER_MERE.md'
CHECKPOINT=ROOT/'CHECKPOINT.json'
def git(*args):
    return subprocess.check_output(['git',*args],text=True).strip()
def update():
    revision=os.getenv('GITHUB_SHA') or git('rev-parse','HEAD')
    if not revision or not all(c in '0123456789abcdef' for c in revision):raise ValueError('invalid revision')
    known=LOG.read_text(encoding='utf-8').splitlines() if LOG.exists() else []
    if any(json.loads(line)['revision']==revision for line in known):
        print('ALREADY_CAPTURED',revision);return
    summary=git('show','-s','--format=%s',revision)
    changed=git('diff-tree','--no-commit-id','--name-only','-r',revision).splitlines()
    changed=[p for p in changed if p.startswith('MOTEUR-BLESSING/labs/RIZ112/')]
    if not changed:print('NO_LAB_PATHS');return
    event={
        'schema':'riz112/auto-git-event/v1',
        'revision':revision,
        'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'commit_summary':summary[:512],
        'changed_paths':changed,
        'provenance':'GITHUB_PUSH_ONLY__NOT_CHAT_TRANSCRIPT',
        'previous_event_sha256':hashlib.sha256(known[-1].encode('utf-8')).hexdigest() if known else None
    }
    LOG.parent.mkdir(parents=True,exist_ok=True)
    with LOG.open('a',encoding='utf-8') as f:
        f.write(json.dumps(event,ensure_ascii=False,sort_keys=True)+'\n')
    note=('\n\n### Synchronisation automatique GitHub — '+event['date_utc']+'\n\n'
         '- Commit source : '+revision+'\n'
         '- Message : '+summary.replace('\n',' ')[:320]+'\n'
         '- Fichiers concernés : '+', '.join(changed[:16])+'\n'
         '- Provenance : événement GitHub push. Ceci ne contient PAS les '
         'messages privés ChatGPT non consignés explicitement.\n')
    with CAHIER.open('a',encoding='utf-8') as f:f.write(note)
    checkpoint=json.loads(CHECKPOINT.read_text(encoding='utf-8'))
    checkpoint['automatic_git_sync']={
        'enabled':True,'last_source_revision':revision,
        'last_verified_time_utc':event['date_utc'],
        'log':'continuity/AUTO_GIT_EVENTS.jsonl',
        'captures_private_chat_automatically':False,
        'automatically_updates_google_docs':False,
        'source_scope':'GitHub pushes in RIZ112 only'
    }
    CHECKPOINT.write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('SYNCED_COMMIT',revision,'FILES',len(changed))
if __name__=='__main__':update()
