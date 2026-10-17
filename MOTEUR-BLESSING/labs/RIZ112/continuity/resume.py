#!/usr/bin/env python3
"""Local continuity preflight for Moteur/continue. No network/background execution.

Running the script verifies the current checkpoint and surfaces the *next* actionable work;
ChatGPT must then execute the next step, not only print a status report.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CANONICAL="Moteur/continue"

def load(rel):return json.loads((ROOT/rel).read_text(encoding="utf8"))
def preflight():
    checkpoint=load("CHECKPOINT.json")
    next_action=load("continuity/NEXT_ACTION.json")
    if checkpoint.get("continuity_code")!=CANONICAL or next_action.get("canonical_trigger")!=CANONICAL:
        raise RuntimeError("Code de reprise non unifié")
    must_exist=["CAHIER_MERE.md","CONTEXTE_CONVERSATIONS.md",
       "CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl","DECISIONS.md",
       "journal/JOURNAL_EVENEMENTS.jsonl","PLAN_SUITE_RIZ112_MATRICE.md",
       "continuity/NEXT_ACTION.json"]
    for rel in must_exist:
       if not (ROOT/rel).is_file():raise RuntimeError("Fichier canonique manquant: "+rel)
    sys.path.insert(0,str(ROOT/'journal'))
    from journal_tool import inspect
    journal=inspect(ROOT/'journal/JOURNAL_EVENEMENTS.jsonl')
    context=[json.loads(x) for x in (ROOT/'CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl').read_text(encoding='utf8').splitlines() if x.strip()]
    if checkpoint['journal']['events']!=len(journal) or checkpoint['journal']['head']!=journal[-1]['digest']:
       raise RuntimeError('Checkpoint non synchronisé avec le journal hash-chaîné')
    if checkpoint.get('continuity',{}).get('context_rows')!=len(context):
       raise RuntimeError('Checkpoint non synchronisé avec le contexte')
    if len(set(x['event_ref'] for x in context))!=len(context):raise RuntimeError('Doublons de contexte')
    return {'trigger':CANONICAL,'checkpoint_stage':checkpoint['stage'],
      'checkpoint_status':checkpoint['status'], 'journal_events':len(journal),
      'context_rows':len(context), 'next_execution':next_action['next_execution_id'],
      'first_action':next_action['first_technical_action'],
      'first_files_to_open':next_action['first_files_to_open'],
      'science':checkpoint['scientific']['status'],
      'instruction':'COMMENCER LE TRAVAIL SUIVANT IMMÉDIATEMENT'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--json',action='store_true')
    args=ap.parse_args();x=preflight()
    if args.json:print(json.dumps(x,ensure_ascii=False,indent=2))
    else:
      print(CANONICAL,'— H'+str(x['checkpoint_stage']))
      print(x['next_execution']+' : '+x['first_action'])
      print('Contexte',x['context_rows'],'messages; journal',x['journal_events'],'événements')
if __name__=='__main__':main()
