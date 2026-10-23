#!/usr/bin/env python3
"""Journal d'événements hash-chaînés RIZ-112 : append-only, audit hors ligne.

La chaîne détecte modifications accidentelles; sans signature/témoin externe,
ce mécanisme NE prouve pas la date ni ne protège contre réécriture complète.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REQUIRED=('id','date','origin','type','summary','evidence','confidence','supersedes')
VALID={'USER_DIRECTIVE','USER_FEEDBACK','ASSISTANT_ACTION','DESIGN_DECISION','HYPOTHESIS',
       'TESTED','FAILED','CORRECTION','SYNC','OPEN_QUESTION','CHECKPOINT',
       'USER_QUESTION','AUDIT'}

class JournalError(ValueError): pass

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def digest(prev:str, event:dict)->str:
    return hashlib.sha256((prev+'\n'+canonical(event)).encode('utf8')).hexdigest()

def inspect(path:Path) -> list[dict]:
    if not path.exists():return []
    rows=[];prev='GENESIS';ids=set()
    for line_no,line in enumerate(path.read_text(encoding='utf8').splitlines(),1):
        try:r=json.loads(line)
        except ValueError as e: raise JournalError(f'ligne {line_no} JSON invalide') from e
        if not isinstance(r,dict) or set(r)!=set(REQUIRED)|{'previous_digest','digest'}:
            raise JournalError(f'ligne {line_no}: schéma altéré')
        event={k:r[k] for k in REQUIRED}
        if r['id'] in ids or r['previous_digest']!=prev or r['digest']!=digest(prev,event):
            raise JournalError(f'ligne {line_no}: doublon ou rupture de chaîne')
        if r['type'] not in VALID or not isinstance(r['summary'],str) or not r['summary'].strip():
            raise JournalError(f'ligne {line_no}: contenu incorrect')
        ids.add(r['id']);rows.append(r);prev=r['digest']
    return rows

def append(path:Path, event:dict) -> str:
    if not isinstance(event,dict) or set(event)!=set(REQUIRED):
        raise JournalError('écritures exigent le schéma exact et aucun hash fourni par appelant')
    if event['type'] not in VALID or not event['summary'] or not isinstance(event['summary'],str):
        raise JournalError('type ou résumé invalide')
    rows=inspect(path)
    if any(r['id']==event['id'] for r in rows): raise JournalError('événement déjà enregistré')
    prev=rows[-1]['digest'] if rows else 'GENESIS'
    out=dict(event,previous_digest=prev,digest=digest(prev,event))
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf8',newline='\n') as f:
        f.write(canonical(out)+'\n')
    if inspect(path)[-1]['digest']!=out['digest']:raise JournalError('écriture pas confirmée')
    return out['digest']

def main():
    p=argparse.ArgumentParser()
    p.add_argument('journal',type=Path)
    p.add_argument('--event-json',type=Path)
    args=p.parse_args()
    if args.event_json:
        e=json.loads(args.event_json.read_text(encoding='utf8'))
        print(append(args.journal,e))
    else:
        events=inspect(args.journal)
        print(json.dumps({'events':len(events),'chain_valid':True,'head':events[-1]['digest'] if events else 'GENESIS'},indent=2))

if __name__=='__main__':main()
